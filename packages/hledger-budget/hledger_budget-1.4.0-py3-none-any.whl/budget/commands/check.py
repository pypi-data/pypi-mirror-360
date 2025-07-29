import sys
from dataclasses import replace

import click
from budget.hledger import bal_budget, bal_csv, prepare_db
from budget.rendering import render
from budget.structures import Args, Database, Summary
from budget.table import ColumnStyle, Table, Text
from budget.utils import eprint

from ._options import common_options


def sum_budgeted(db: Database, commodity: str) -> Summary:
    summed = Summary("total", "", commodity, 0, 0)
    for summary in db.iter(commodity=commodity):
        if not summary.budget:
            continue

        summed.balance += summary.balance
        if summed.budget is None:
            summed.budget = summary.budget
        else:
            summed.budget += summary.budget
    return summed


def sum_missing_spendings(db: Database, commodity: str) -> Summary:
    fore = Summary("forecast", "", commodity, 0, 0)

    for summary in db.iter(commodity=commodity):
        if not summary.budget:
            continue

        if summary.budget < summary.balance:
            continue

        fore.balance += summary.budget - summary.balance

    return fore


@click.command()
@common_options
@click.argument("assets", nargs=-1)
@click.option(
    "-t",
    "--title",
    default="Budget Verification",
    help="report title",
)
@click.option(
    "--no-auto-excludes",
    is_flag=True,
    default=False,
    help="disable automatic exclusions of unbudgeted and assets accounts from the budget",
)
@click.pass_obj
def check(args: Args, title, assets, no_auto_excludes, **kwargs):
    """Check correctness of budget against available assets."""
    if not assets:
        return

    args = replace(args, **kwargs)

    # This is what users actually want even if they don't know it :)
    #
    # Suppose that we have 2 accounts for our cash:
    #   - assets:bank:checking
    #   - assets:bank:savings
    # Each month we save some cash by transfering it from checking to savings.
    # Hledger includes savings account in budget report, but it also
    # includes its parent: assets:bank. Now, assets:bank:checking quietly
    # contributes to assets:bank (see `hledger bal -E` for proof) and to
    # the sum of expenses. The problem is that checking accounts balance is a
    # result of many transactions which don't contribute to the "budget" or
    # "spending" report, like income.
    if not no_auto_excludes:
        args.excludes.extend(assets)
        args.excludes.append("unbudgeted")

    db = prepare_db(bal_budget(args))

    ass_args = replace(
        args,
        includes=assets,
        excludes=[],
        flags={"cumulative": True, "historical": True},
    )

    assets_db = prepare_db(bal_csv(ass_args))

    result = True

    def make_cell(msg, cond: bool, errmsg: str | None = None):
        nonlocal result
        result &= cond

        t = Text(str(msg))
        if not cond:
            t.style = "error"
            if errmsg:
                t.metadata["message"] = errmsg
        return t

    if not db.commodities:
        eprint("No postings to check!")
        sys.exit(1)

    t = Table(title=title)
    t.add_column(
        "Money available",
        "Remaining budgeted spendings",
        "Budgeted spendings",
        "Total forecasted spendings",
        "Total budget",
        "Unbudgeted funds",
        header="Report",
    )

    for commodity in db.commodities:
        spendings = sum_budgeted(db, commodity)
        if spendings.budget is None:
            eprint(f"No budgeted spendings for {commodity}.")
            eprint("Do you have any periodic transactions for this commodity?")
            result = False
            continue

        missing_spendings = sum_missing_spendings(db, commodity)
        forecast = spendings.balance + missing_spendings.balance

        # NOTE: in case there's no assets in a given currency, assets_db.iter()
        # will produce empty iterator, and sum() will return integer (not Decimal) 0.
        # This is the case when you budget in a currency, but rely on auto
        # currency conversion done by bank.
        cash = sum(summary.balance for summary in assets_db.iter(commodity=commodity))

        unbudgeted = cash - missing_spendings.balance

        t.add_column(
            f"{cash:.2f}",
            make_cell(
                f"{missing_spendings.balance:.2f}",
                missing_spendings.balance <= cash,
                "Not enough money for remaining spendings.",
            ),
            f"{spendings.balance:.2f}",
            make_cell(
                f"{forecast:.2f}",
                forecast <= cash + spendings.balance,
                "Insufficient funds for forecasted budgeted and unbudgeted spendings.",
            ),
            f"{spendings.budget:.2f}",
            make_cell(f"{unbudgeted:.2f}", unbudgeted >= 0, "Over-budgeting."),
            header=commodity,
            style=ColumnStyle(justify="right"),
        )

    render(args.output_type, t)

    sys.exit(int(not result))
