"""
    lager.gpo.commands

    Commands for setting output on gateway GPO lines
"""
import json
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal

_LEVEL_CHOICES = click.Choice(('LOW', 'HIGH', 'ON', 'OFF'), case_sensitive=False)

@click.command(name='gpo')
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('NETNAME', required=True)
@click.argument('LEVEL', type=_LEVEL_CHOICES)
@click.pass_context
def gpo(ctx, gateway, dut, netname, level):
    """
        Sets GPO level (0 for low, 1 for high)
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
        args=[json.dumps(dict(netname=netname, action='output', level=level))],
    )