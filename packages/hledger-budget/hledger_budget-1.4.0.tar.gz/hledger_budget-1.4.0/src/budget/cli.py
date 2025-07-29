#!/usr/bin/env python3

import click

from budget import __version__ as _version
from budget.commands.balance import balance
from budget.commands.check import check
from budget.structures import Args


def print_version(ctx, _param, value):
    if not value or ctx.resilient_parsing:
        return

    print(f"hledger-budget {_version}")
    ctx.exit()


@click.group()
@click.option("-f", "--file", help="input file")
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
def cli(**kwargs):
    """Budget helper for hledger"""
    args = Args(**kwargs)
    ctx = click.get_current_context()
    ctx.obj = args


cli.add_command(balance)
cli.add_command(check)
