from dataclasses import replace
from typing import Any, Iterable

import click

from budget.hledger import bal_budget, prepare_db
from budget.rendering import render
from budget.structures import Args, Summary
from budget.table import ColumnStyle, Table
from budget.utils import flatten

from ._options import common_options


def add_to_row(
    s: Summary, commodities: list[str], rows: dict[str, dict[str, Summary | None]]
):
    if s.account not in rows:
        rows[s.account] = {comm: None for comm in commodities}
    rows[s.account][s.commodity] = s


def collect_rows(
    summaries: Iterable[Summary], commodities: list[str]
) -> dict[str, dict[str, Summary | None]]:
    rows: dict[str, dict[str, Summary | None]] = {}
    for summary in summaries:
        add_to_row(summary, commodities, rows)
    return rows


def to_cells(s: Summary | None) -> tuple[str, str]:
    if not s:
        return "", ""

    if not s.budget:
        return f"{s.balance:.2f}", ""

    perc = round(s.balance / s.budget * 100)
    return f"{s.balance:.2f}", f"{perc}% of {s.budget:.2f}"


@click.command()
@common_options
@click.option("-t", "--title", default="Budget: {commodity}", help="report title")
@click.option(
    "--no-auto-excludes",
    is_flag=True,
    default=False,
    help="disable automatic exclusions of unbudgeted accounts",
)
@click.option(
    "-u",
    "--unbudgeted",
    is_flag=True,
    default=False,
    help="show accounts without budget goals",
)
@click.option(
    "-U",
    "--only-unbudgeted",
    is_flag=True,
    default=False,
    help="show only accounts without budget goals; implies --unbudgeted",
)
@click.option(
    "-E",
    "--empty",
    is_flag=True,
    default=False,
    help="show accounts which have no budget or balance",
)
@click.option(
    "--no-total",
    is_flag=True,
    default=False,
    help="don't show a summary of budget and spendings",
)
@click.pass_obj
def balance(
    args: Args,
    title,
    no_auto_excludes,
    unbudgeted,
    only_unbudgeted,
    empty,
    no_total,
    **kwargs,
):
    """Show balance report together with budget goals defined by periodic transactions.

    This report differs from ordinary 'hledger balance --budget' by showing
    only accounts with budget goals without aggregating goals of subaccounts.

    When run with --unbudgeted, report will also present accounts without
    budget goals. Side effect is that due to the presence of unbudgeted
    accounts, balances for some of budgeted parent accounts will change to 0.

    Report is created for all accounts, but you should probably exclude all
    accounts which are transaction sources (typically "assets:bank:checking"
    and so on).
    """
    if only_unbudgeted:
        unbudgeted = True

    args = replace(args, **kwargs)

    # This is counter-intuitive: why we use the value of --unbudgeted instead
    # of --empty? That's because 'hledger --budget' hides subaccounts without
    # budget, so if we want to show unbudgeted accounts, we must use 'hledger
    # --empty'.
    #
    # Side effect is that our de-aggregation now has a complete list of
    # accounts, so main parents will always have 0 balance, even with
    # additional exclusions (because hledger will take exclusions into account
    # and re-calculate parents' balances)
    args.flags["empty"] = unbudgeted

    if not no_auto_excludes:
        args.excludes.append("unbudgeted")

    db = prepare_db(bal_budget(args), commodities_order=kwargs["commodities"])

    matchers: dict[str, Any] = {}
    if not unbudgeted:
        matchers["budget"] = True
    if only_unbudgeted:
        matchers["budget"] = False
    if not empty:
        matchers["_"] = lambda x: x.balance or x.budget

    summaries = collect_rows(db.iter(**matchers), db.commodities)
    total: list[Summary] = [Summary("Total", "", c) for c in db.commodities]

    t = Table(title=title.format(commodity=", ".join(db.commodities)))
    t.add_column(header="Account", *summaries.keys())
    for i, comm in enumerate(db.commodities):
        cbal = []
        cexe = []

        for summary_per_comm in summaries.values():
            summary = summary_per_comm[comm]
            bal, execution = to_cells(summary)
            cbal.append(bal)
            cexe.append(execution)
            if summary:
                total[i].balance += summary.balance
                total[i].budget += summary.budget

        t.add_column(
            *cbal, header=["Balance", comm], style=ColumnStyle(justify="right")
        )
        t.add_column(
            *cexe, header=["Budget Execution", comm], style=ColumnStyle(justify="right")
        )

    if not no_total:
        footer = flatten([to_cells(t) for t in total])
        t.set_footer("Total", *footer)

    render(args.output_type, t)
