"""
    lager.serial_ports.commands

    Listing serial ports
"""
import click
from ..context import get_default_gateway

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
def serial_ports(ctx, gateway, dut):
    """
        List the serial ports attached to a DUT
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.serial_ports(gateway)
    style = ctx.obj.style
    for port in resp.json()['serial_ports']:
        if port['device'] == '/dev/ttyS0':
            continue
        click.echo('{} - {}'.format(style(port['device'], fg='green'), port['description']))
