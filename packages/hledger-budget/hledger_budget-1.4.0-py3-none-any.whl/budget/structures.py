from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable

from budget.date import first_of_this_month, tomorrow


@dataclass
class Args:
    file: str | None = None
    begin: str | None = None
    end: str | None = None
    period: str | None = None
    commodities: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)
    flags: dict[str, bool | str] = field(default_factory=dict)
    output_type: str = ""

    def __post_init__(self):
        def to_list(val):
            if isinstance(val, str):
                return [str]
            if isinstance(val, tuple):
                return list(val)
            return val

        self.commodities = to_list(self.commodities)
        self.includes = to_list(self.includes)
        self.excludes = to_list(self.excludes)

        if not self.begin and not self.end and not self.period:
            self.begin = first_of_this_month()

        if not self.end and not self.period:
            # 1. hledger's --end is exclusive and we want to show today's transactions
            # 2. This has side effects: when there are no transactions, or only
            #    periodic transactions in journal file, hledger won't calculate end date
            #    and won't show the budget, because it would be infinity (hledger uses
            #    date of last transaction as default --end). This allows it to show the
            #    budget even if no transactions were made.
            self.end = tomorrow()


@dataclass
class Summary:
    account: str
    period: str
    commodity: str
    balance: Decimal | int = 0
    budget: Decimal | int = 0

    def __post_init__(self):
        if isinstance(self.balance, (str, int)):
            self.balance = Decimal(self.balance)
        if isinstance(self.budget, (str, int)):
            self.budget = Decimal(self.budget)


@dataclass
class Database:
    summaries: list[Summary] = field(default_factory=list)
    periods: list[str] = field(default_factory=list)
    commodities: list[str] = field(default_factory=list)

    def insert(self, summary: Summary):
        self.summaries.append(summary)

        if summary.period not in self.periods:
            self.periods.append(summary.period)

        if summary.commodity not in self.commodities:
            self.commodities.append(summary.commodity)

    def insert_many(self, summaries: Iterable[Summary]):
        for summary in summaries:
            self.insert(summary)

    def iter(self, **matchers):
        matchers_ = []
        for name, matchval in matchers.items():
            if matcher := self._create_matcher(name, matchval):
                matchers_.append(matcher)

        for summary in self.summaries:
            if all(m(summary) for m in matchers_):
                yield summary

    def _create_matcher(self, attr, matchval):
        if matchval is None:
            return None

        if callable(matchval):
            return matchval

        if matchval in (True, False):
            return lambda x: bool(getattr(x, attr)) is matchval

        if isinstance(matchval, (list, tuple)):
            return lambda x: getattr(x, attr) in matchval

        return lambda x: getattr(x, attr) == matchval
