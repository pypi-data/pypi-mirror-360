import csv
import os
import subprocess
from io import StringIO
from typing import Iterable

from budget.structures import Args, Database, Summary


def bal_csv(args: Args):
    cmd = ["hledger"]

    if args.file:
        cmd.extend(("--file", args.file))

    cmd.extend(["balance", "--no-total", "--layout", "bare", "-O", "csv"])

    if args.begin:
        cmd.extend(("--begin", args.begin))
    if args.end:
        cmd.extend(("--end", args.end))
    if args.period:
        cmd.extend(("--period", args.period))

    for name, value in args.flags.items():
        if value is True:
            cmd.append(f"--{name}")
        elif value is False:
            continue
        else:
            cmd.extend((f"--{name}", str(value)))
    for excl in args.excludes:
        cmd.append(f"not:{excl}")
    if args.commodities:
        expr = " or ".join(f"cur:{comm}" for comm in args.commodities)
        cmd.append(f"expr:{expr}")

    cmd.extend(args.includes)

    env = os.environ.copy()
    env.pop("LANG", None)
    cp = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    f = StringIO(cp.stdout)
    yield from csv.reader(f, delimiter=",")


def bal_budget(args: Args):
    args.flags["budget"] = True
    yield from bal_csv(args)


def deaggregate(summaries: Iterable[Summary]):
    revsummaries = sorted(summaries, reverse=True, key=lambda r: r.account)
    for i, summary in enumerate(revsummaries):
        for parent in revsummaries[i + 1 :]:
            if (
                summary.account.startswith(parent.account + ":")
                and summary.commodity == parent.commodity
            ):
                parent.balance -= summary.balance
                if parent.budget >= summary.budget:
                    parent.budget -= summary.budget


def prepare_db(rows, commodities_order=None) -> Database:
    if commodities_order is None:
        commodities_order = []

    db = Database(commodities=list(commodities_order))
    header = next(rows)

    for row in rows:
        # csv format: account, commodity, p1bal, [p1bud], p2bal, [p2bud], ...
        account = row[0]
        commodity = row[1]

        i = 2
        while i < len(row):
            period = header[i]
            balance = row[i]
            budget = 0

            if i + 1 < len(row) and header[i + 1] == "budget":
                budget = row[i + 1]
                i += 1

            i += 1
            s = Summary(account, period, commodity, balance, budget)

            # hledger shows previously budgeted accounts as empty, but doesn't
            # include their commodity when there's no budget for them in
            # current time period.
            if not s.commodity and not s.balance and not s.budget:
                continue

            db.insert(s)

    if commodities_order is None:
        commodities_order = []

    for period in db.periods:
        deaggregate(db.iter(period=period))

    return db
