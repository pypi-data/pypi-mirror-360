"""
    lager.arm.commands

    Arm commands
"""
import click
from ..context import get_default_gateway
from ..context import get_impl_path
from ..python.commands import run_python_internal

def run_command(ctx, dut, args):
    if dut is None:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx,
        get_impl_path('actuate.py'),
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
        args=args,
    )

@click.command(hidden=True)
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.argument('NETNAME', required=True)
def actuate(ctx, dut, netname):
    """
        Actuate a net
    """
    run_command(ctx, dut, (netname,))
