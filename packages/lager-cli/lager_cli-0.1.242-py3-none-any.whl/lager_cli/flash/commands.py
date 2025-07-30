"""
    lager.flash.commands

    Commands for flashing a DUT
"""
import itertools
import click
from ..context import get_default_gateway
from ..util import stream_output
from ..paramtypes import BinfileType

def do_flash(session, gateway, hexfile, binfile, elffile, preverify, verify, run=False, mcu=None):
    """
        Perform the actual flash operation
    """
    files = list(zip(itertools.repeat('hexfile'), [open(path, 'rb') for path in hexfile]))
    files.extend(
        zip(itertools.repeat('binfile'), [open(binf.path, 'rb') for binf in binfile])
    )
    files.extend(
        zip(itertools.repeat('binfile_address'), [binf.address for binf in binfile])
    )
    files.extend(
        zip(itertools.repeat('elffile'), [open(path, 'rb') for path in elffile])
    )
    files.append(('preverify', preverify))
    files.append(('verify', verify))
    files.append(('force', False))
    files.append(('run', run))
    if mcu:
        files.append(('mcu', mcu))

    return session.flash_dut(gateway, files=files)


@click.command(hidden=True)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option(
    '--hexfile',
    multiple=True, type=click.Path(exists=True),
    help='Hexfile(s) to flash. May be passed multiple times; files will be flashed in order.')
@click.option(
    '--binfile',
    multiple=True, type=BinfileType(exists=True),
    help='Binfile(s) to flash. Syntax: --binfile `<filename>,<address>` '
         'May be passed multiple times; files will be flashed in order.')
@click.option(
    '--elffile',
    multiple=True, type=click.Path(exists=True),
    help='Elf file(s) to flash. May be passed multiple times; files will be flashed in order.')
@click.option('--run/--no-run', help='Run after flashing', default=False, show_default=True)
@click.option(
    '--preverify/--no-preverify',
    help='If true, only flash target if image differs from current flash contents',
    default=True, show_default=True)
@click.option('--verify/--no-verify', help='Verify image successfully flashed', default=True, show_default=True)
@click.option('--mcu', required=False, default=None, help='MCU to target', type=click.INT)
def flash(ctx, gateway, dut, hexfile, binfile, elffile, run, preverify, verify, mcu):
    """
        Flash a DUT connected to a gateway with 1 or more bin or hex files
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    session = ctx.obj.session

    resp = do_flash(session, gateway, hexfile, binfile, elffile, preverify, verify, run, mcu)
    stream_output(resp)
