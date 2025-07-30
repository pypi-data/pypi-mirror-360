"""
    lager.db.commands

    DB commands
"""
import click
from ..context import get_default_gateway
import time
from ..context import get_impl_path
from ..python.commands import run_python_internal
import datetime

@click.group()
def db():
    """
        Lager db commands
    """
    pass


@db.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--created-at', type=click.DateTime(), required=False, default=datetime.datetime.utcnow())
@click.option('--tag', required=False, multiple=True)
def insert(ctx, dut, created_at, tag):
    """
    SSH to the specified gateway
    """
    if dut is None:
        dut = get_default_gateway(ctx)


    run_python_internal(
        ctx,
        get_impl_path('db_insert.py'),
        dut,
        image='',
        env=(),
        passenv=(),
        kill=False,
        download=(),
        allow_overwrite=False,
        signum='SIGTERM',
        timeout=0,
        detach=False,
        port=(),
        org=None,
        args=(created_at, tag),
    )
