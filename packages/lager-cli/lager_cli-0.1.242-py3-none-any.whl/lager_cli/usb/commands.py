"""
    lager.usb.commands

    Commands for USB interaction
"""
import json
import click
from ..context import get_impl_path
from ..python.commands import run_python_internal

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('DEVICE', required=False)
@click.argument('ACTION', required=False, type=click.Choice(['on', 'off', 'toggle']))
def usb(ctx, gateway, dut, device, action):
    """
        Control USB ports on a DUT
    """
    gateway = gateway or dut
    run_python_internal(
        ctx,
        get_impl_path('usb.py'),
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
        args=[json.dumps(dict(device=device, action=action))],
    )
