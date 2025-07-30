"""
    lager.debug.commands

    Debug an elf file
"""
import itertools
import click
from ..context import get_default_gateway
from ..debug.gdb import debug
from ..gateway.commands import _status
from ..paramtypes import MemoryAddressType, HexArrayType
from ..debug.tunnel import serve_tunnel, serve_local_tunnel
from ..openocd.commands import run_openocd_tunnel
from ..context import get_impl_path
from ..python.commands import run_python_internal
from ..paramtypes import BinfileType
import trio
from ..debug.tunnel import serve_tunnel, serve_local_tunnel
from ..util import StreamDatatypes
import json

@click.group(name='debug')
def _debug():
    """
        Lager debug commands
    """
    pass

@_debug.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, default=None, help='MCU to query', type=click.INT)
def status(ctx, gateway, dut, mcu):
    gateway = gateway or dut
    _status(ctx, gateway, mcu)

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to connect')
@click.option('--force/--no-force', is_flag=True, default=True, help='Disconnect debugger before reconnecting. If not set, connect will fail if debugger is already connected. Cannot be used with --ignore-if-connected', show_default=True)
@click.option('--ignore-if-connected', is_flag=True, default=False, help='If debugger is already connected, skip connection attempt and exit with success. Cannot be used with --force', show_default=True)
@click.option('--halt/--no-halt', is_flag=True, default=True, help='Halt the device when connecting', show_default=True)
def connect(ctx, dut, mcu, force, ignore_if_connected, halt):
    if force and ignore_if_connected:
        click.secho('Cannot specify --force and --ignore-if-connected', fg='red')
        ctx.exit(1)

    if dut is None:
        dut = get_default_gateway(ctx)
    session = ctx.obj.session
    if halt:
        attach = 'reset-halt'
    else:
        attach = 'attach'

    resp = session.debug_connect(dut, mcu, force, ignore_if_connected, attach).json()
    if resp.get('start') == 'ok':
        click.secho('Connected!', fg='green')
    elif resp.get('already_running') == 'ok':
        click.secho('Debugger already connected, ignoring', fg='green')

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to disconnect')
def disconnect(ctx, dut, mcu):
    if dut is None:
        dut = get_default_gateway(ctx)
    session = ctx.obj.session
    session.debug_disconnect(dut, mcu).json()
    click.secho('Disconnected!', fg='green')

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to erase')
@click.argument('start_addr', required=False, type=MemoryAddressType())
@click.argument('length', required=False, type=MemoryAddressType())
def erase(ctx, dut, mcu, start_addr, length):
    if dut is None:
        dut = get_default_gateway(ctx)
    session = ctx.obj.session
    out = session.debug_erase(dut, mcu, start_addr, length).json()
    print(out['output'])
    if 'Erasing done.' in out['output']:
        click.secho('Erased!', fg='green')
    else:
        click.secho('Erasing failed', fg='red')
        ctx.exit(1)

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to erase')
@click.argument('start_addr', type=MemoryAddressType())
@click.argument('length', type=MemoryAddressType())
def memrd(ctx, dut, mcu, start_addr, length):
    if dut is None:
        dut = get_default_gateway(ctx)
    session = ctx.obj.session
    out = session.debug_read(dut, mcu, start_addr, length).json()
    print(out['output'])


@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to erase')
@click.option('--size', required=True, type=click.Choice(['1', '2', '4']), help='Number of bytes to write')
@click.argument('start_addr', type=MemoryAddressType())
@click.argument('data')
def memwr(ctx, dut, mcu, size, start_addr, data):
    if dut is None:
        dut = get_default_gateway(ctx)

    if data.startswith('0x') or data.startswith('0X'):
        data = data[2:]

    session = ctx.obj.session
    out = session.debug_write(dut, mcu, int(size, 10), start_addr, data).json()
    print(out['output'])


@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, help='MCU to disconnect')
@click.option(
    '--hexfile',
    type=click.Path(exists=True),
    help='Hexfile to flash.')
@click.option(
    '--binfile',
    multiple=True, type=BinfileType(exists=True),
    help='Binfile(s) to flash. Syntax: --binfile `<filename>,<address>` '
         'May be passed multiple times; files will be flashed in order.')
def flash(ctx, dut, mcu, hexfile, binfile):
    if dut is None:
        dut = get_default_gateway(ctx)
    session = ctx.obj.session
    files = []
    if hexfile:
        files.append(('hexfile', open(hexfile, 'rb').read()),)
    elif binfile:
        files.extend(
            zip(itertools.repeat('binfile'), [open(binf.path, 'rb') for binf in binfile])
        )
        files.extend(
            zip(itertools.repeat('binfile_address'), [binf.address for binf in binfile])
        )

    if mcu:
        files.append(('mcu', mcu))

    output = session.debug_flash(dut, files).json()['output']
    print(output)
    if 'Downloading file [/tmp/jlink_hexfile.hex]...' in output and 'O.K.' in output:
        click.secho('Flashed!', fg='green')
    elif 'Downloading file [/tmp/jlink_binfile.bin]...' in output and 'O.K.' in output:
        click.secho('Flashed!', fg='green')
    else:
        click.secho('Flashing failed!', fg='red')
        ctx.exit(1)

RTT_BASE_PORT = 9090

@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, default=0, type=click.INT, help='MCU number')
@click.option('--host', default='localhost', help='interface for telnet to bind. '
              'Use --host \'*\' to bind to all interfaces.', show_default=True)
def rtt(ctx, dut, mcu, host):
    if dut is None:
        dut = get_default_gateway(ctx)

    port = RTT_BASE_PORT + mcu
    run_openocd_tunnel(ctx, host, None, dut, True, port)


@_debug.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False, default=0, type=click.INT, help='MCU number')
@click.option('--halt/--no-halt', is_flag=True, help='Halt the DUT after reset. Default: do not halt', default=False, show_default=True)
def reset(ctx, dut, mcu, halt):
    if dut is None:
        dut = get_default_gateway(ctx)

    session = ctx.obj.session
    if halt:
        attach = 'reset-halt'
    else:
        attach = 'reset'

    run_python_internal(
        ctx,
        get_impl_path('gdb_reset.py'),
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
        args=(halt, ),
    )

# gdbserver

def _run_gdbserver_cloud(ctx, host, port, gateway, socktype):
    connection_params = ctx.obj.websocket_connection_params(socktype=socktype, gateway_id=gateway)
    try:
        trio.run(serve_tunnel, host, port, connection_params, 'GDB')
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start gdbserver on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

def _run_gdbserver_local(ctx, host, port, gateway):
    try:
        trio.run(serve_local_tunnel, ctx.obj.session, gateway, host, port, True)
    except PermissionError as exc:
        if port < 1024:
            click.secho(f'Permission denied for port {port}. Using a port number less than '
                        '1024 typically requires root privileges.', fg='red', err=True)
        else:
            click.secho(str(exc), fg='red', err=True)
        if ctx.obj.debug:
            raise
    except OSError as exc:
        click.secho(f'Could not start gdbserver on port {port}: {exc}', fg='red', err=True)
        if ctx.obj.debug:
            raise

@_debug.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--host', default='localhost', help='interface for gdbserver to bind.', show_default=True)
@click.option('--port', default=3333, help='Port for gdbserver', show_default=True)
@click.option('--local', is_flag=True, default=False, help='Connect to gateway via local network', show_default=True)
def gdbserver(ctx, gateway, dut, host, port, local):
    """
    Establish a proxy to GDB server on gateway.
    """
    from ..context import get_default_gateway

    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    socktype = 'jl-tunnel'

    if local:
        from ..debug.tunnel import serve_local_tunnel
        trio.run(serve_local_tunnel, ctx.obj.session, gateway, host, port, True)
    else:
        from ..debug.tunnel import serve_tunnel
        connection_params = ctx.obj.websocket_connection_params(socktype=socktype, gateway_id=gateway)
        trio.run(serve_tunnel, host, port, connection_params, 'GDB')

@_debug.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
def testcmd(ctx, gateway, dut,):
    from ..context import get_default_gateway
    from ..context import get_impl_path
    from ..python.commands import run_python_internal_get_output

    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    final_context = run_python_internal_get_output(
        ctx,
        get_impl_path('do_stuff.py'),
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
    print(f"Got json output: {json.loads(final_context)}")
