"""
    lager.serial_ports.commands

    Listing serial ports
"""
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal

@click.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
def hello(ctx, dut):
    """
        Say hello to gateway
    """
    run_python_internal(
        ctx,
        get_impl_path('hello.py'),
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
        args=(),
    )
