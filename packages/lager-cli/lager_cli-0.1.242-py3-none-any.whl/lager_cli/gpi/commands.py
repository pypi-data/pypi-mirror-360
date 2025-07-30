"""
    lager.gpi.commands

    Commands for reading input from gateway GPI lines
"""
import json
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal

@click.command(name='gpi')
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('NETNAME', required=True)
@click.pass_context
def gpi(ctx, gateway, dut, netname):
    """
        Returns GPI level (0 for low, 1 for high)
    """
    gateway = gateway or dut
    run_python_internal(
        ctx,
        get_impl_path('gpio.py'),
        gateway,
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
        args=[json.dumps(dict(netname=netname, action='input', level=None))],
    )
