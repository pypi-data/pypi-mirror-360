import itertools
from dataclasses import dataclass
from decimal import Decimal

from budget.console import console, econsole

rprint = console.print


@dataclass
class Amount:
    balance: Decimal = Decimal(0)
    budget: Decimal = Decimal(0)


def eprint(*a, **kw):
    kw.setdefault("style", "error")
    econsole.print(*a, **kw)


def flatten(val):
    return list(itertools.chain.from_iterable(val))
