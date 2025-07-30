"""
    lager.gpio.commands

    Commands for manipulating gateway GPIO lines
"""
import json
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal

_LEVEL_CHOICES = click.Choice(('LOW', 'HIGH', 'ON', 'OFF'), case_sensitive=False)

@click.group(hidden=True)
def gpio():
    """
        Lager gpio commands
    """
    pass

def run_gpio(ctx, gateway, netname, action, level):
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
        args=[json.dumps(dict(netname=netname, action=action, level=level))],
    )

@gpio.command(name='input')
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('NETNAME', required=True)
@click.pass_context
def input_(ctx, gateway, dut, netname):
    """
        Returns GPIO level (0 for low, 1 for high)
    """
    gateway = gateway or dut
    run_gpio(ctx, gateway, netname, 'input', None)

@gpio.command()
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('NETNAME', required=True)
@click.argument('LEVEL', type=_LEVEL_CHOICES)
@click.pass_context
def output(ctx, gateway, dut, netname, level):
    """
        Sets GPIO level (0 for low, 1 for high)
    """
    gateway = gateway or dut
    run_gpio(ctx, gateway, netname, 'output', level)
