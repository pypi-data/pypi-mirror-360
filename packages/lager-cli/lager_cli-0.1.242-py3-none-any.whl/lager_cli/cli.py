"""
    lager.cli

    Command line interface entry point
"""
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import trio
    import lager_trio_websocket

import os
import urllib.parse
import sys

import traceback
import click

from . import __version__
from .config import read_config_file
from .context import LagerContext

from .gateway.commands import _gateway
from .adc.commands import adc
from .ble.commands import ble
from .debug.commands import _debug
from .setter.commands import setter
from .getter.commands import getter
from .lister.commands import lister
from .auth import load_auth
from .auth.commands import login, logout
from .canbus.commands import canbus
from .chip_erase.commands import chip_erase
from .job.commands import job
from .devenv.commands import devenv
from .exec.commands import exec_
from .flash.commands import flash
from .run.commands import run
from .erase.commands import erase
from .reset.commands import reset
from .uart.commands import uart
from .testrun.commands import testrun
from .connect.commands import connect, disconnect
from .gpio.commands import gpio
from .openocd.commands import openocd
from .python.commands import python
from .wifi.commands import _wifi
from .serial_ports.commands import serial_ports
from .webcam.commands import webcam
from .grafana.commands import grafana
from .pigpio.commands import pigpio
from .spi.commands import spi
from .i2c.commands import i2c
from .pip.commands import pip
# from .net.commands import net, analog
from .net.analog_commands import analog
from .net.logic_commands import logic
from .net.bus_commands import bus
from .net.supply_commands import supply
from .net.supply_tui import supply_tui
from .net.battery_commands import battery
from .net.nets_commands import nets, create_instrument, probe_instruments, list_instruments
from .rtt.commands import rtt
from .usb.commands import usb
from .hello.commands import hello
from .arm.commands import arm
from .ssh.commands import ssh
from .db.commands import db
from .tc.commands import tc
from .actuate.commands import actuate
from .dac.commands import dac
from .gpi.commands import gpi
from .gpo.commands import gpo

def _decode_environment():
    for key in os.environ:
        if key.startswith('LAGER_'):
            os.environ[key] = urllib.parse.unquote(os.environ[key])

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', 'see_version', is_flag=True, help='See package version')
@click.option('--debug', 'debug', is_flag=True, help='Show debug output', default=False)
@click.option('--colorize', 'colorize', is_flag=True, help='Color output', default=False)
@click.option('--version-check/--no-version-check', is_flag=True, help='Check for new version on PyPI', default=True)
@click.option('--interpreter', '-i', required=False, default=None, help='Select a specific interpreter / user interface', hidden=True)
def cli(ctx=None, see_version=None, debug=False, colorize=False, version_check=True, interpreter=None):
    """
        Lager CLI
    """
    if os.getenv('LAGER_DECODE_ENV'):
        _decode_environment()

    if see_version:
        click.echo(__version__)
        click.get_current_context().exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    else:
        os_args = sys.argv[1:]
        help_invoked = '--help' in os_args
        skip_auth = ctx.invoked_subcommand in ('login', 'logout', 'set', 'get', 'devenv', 'exec') or help_invoked
        setup_context(ctx, debug, colorize, skip_auth, interpreter)

cli.add_command(_gateway)
cli.add_command(adc)
cli.add_command(ble)
cli.add_command(_debug)
cli.add_command(setter)
cli.add_command(getter)
cli.add_command(lister)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(canbus)
cli.add_command(chip_erase)
cli.add_command(job)
cli.add_command(devenv)
cli.add_command(exec_)
cli.add_command(flash)
cli.add_command(run)
cli.add_command(erase)
cli.add_command(reset)
cli.add_command(uart)
cli.add_command(testrun)
cli.add_command(connect)
cli.add_command(disconnect)
cli.add_command(gpio)
cli.add_command(openocd)
cli.add_command(python)
cli.add_command(_wifi)
cli.add_command(serial_ports)
cli.add_command(webcam)
cli.add_command(grafana)
cli.add_command(pigpio)
cli.add_command(spi)
cli.add_command(i2c)
cli.add_command(pip)
cli.add_command(analog)
cli.add_command(logic)
cli.add_command(bus)
cli.add_command(supply)
cli.add_command(supply_tui)
cli.add_command(battery)
cli.add_command(nets)
cli.add_command(create_instrument)
cli.add_command(probe_instruments)
cli.add_command(list_instruments)
cli.add_command(rtt)
cli.add_command(usb)
cli.add_command(hello)
cli.add_command(arm)
cli.add_command(ssh)
cli.add_command(db)
cli.add_command(tc)
cli.add_command(actuate)
cli.add_command(dac)
cli.add_command(gpi)
cli.add_command(gpo)

def setup_context(ctx, debug, colorize, skip_auth, interpreter):
    """
        Ensure the user has a valid authorization
    """
    auth = None
    if not skip_auth:
        try:
            auth = load_auth()
        except Exception:  # pylint: disable=broad-except
            trace = traceback.format_exc()
            click.secho(trace, fg='red')
            click.echo('Something went wrong. Please run `lager logout` followed by `lager login`')
            click.echo('For additional assistance please send the above traceback (in red) to support@lagerdata.com')
            click.get_current_context().exit(0)

        if not auth:
            click.echo('Please login using `lager login` first')
            click.get_current_context().exit(1)

    config = read_config_file()
    ctx.obj = LagerContext(
        ctx=ctx,
        auth=auth,
        defaults=config['LAGER'],
        debug=debug,
        style=click.style if colorize else lambda string, **kwargs: string,
        interpreter=interpreter,
    )
