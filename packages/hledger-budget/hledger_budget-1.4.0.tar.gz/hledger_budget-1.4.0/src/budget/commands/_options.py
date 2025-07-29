import click

from budget.rendering import OutputType

_COMMON_OPTS = [
    click.option(
        "-i",
        "--budget-include",
        "includes",
        multiple=True,
        default=[],
        help="include accounts for budgeting. When not set, all accounts are included",
    ),
    click.option(
        "-x",
        "--budget-exclude",
        "excludes",
        multiple=True,
        default=[],
        help="exclude accounts for budgeting.",
    ),
    click.option(
        "-c",
        "--commodity",
        "commodities",
        multiple=True,
        default=[],
        help="include only selected currencies",
    ),
    click.option(
        "-b",
        "--begin",
        default=None,
        help="include postings since this date (default: begin of current month, if no other time period is set)",
    ),
    click.option(
        "-e",
        "--end",
        default=None,
        help="include postings until this date",
    ),
    click.option(
        "-p",
        "--period",
        default=None,
        help="time period for which report should be generated",
    ),
    click.option(
        "-O",
        "--output-type",
        type=click.Choice(tuple(ot.value for ot in OutputType)),
        default="rich",
        help="output-type",
    ),
]


def common_options(fn):
    for opt in reversed(_COMMON_OPTS):
        fn = opt(fn)
    return fn
