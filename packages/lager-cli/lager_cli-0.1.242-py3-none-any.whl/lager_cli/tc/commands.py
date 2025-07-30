"""
    lager.tc.commands

    TC (thermocouple) commands
"""

import click
from ..context import get_default_gateway
from ..context import get_impl_path
from ..python.commands import run_python_internal

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('NET', required=True)
def tc(ctx, gateway, dut, net):
    """
        Read the thermocouple for a net the gateway. Result is in degrees C
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    run_python_internal(
        ctx,
        get_impl_path('tc.py'),
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
        args=(net,),
    )

