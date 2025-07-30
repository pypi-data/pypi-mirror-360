"""
    Logic commands
"""
import json
import click
from texttable import Texttable
from ..context import get_default_gateway
from ..context import get_impl_path
from ..python.commands import run_python_internal

def channel_num(mux, mapping):
    point = mux['scope_points'][0][1]
    if mux['role'] == 'analog':
        return ord(point) - ord('A') + 1
    if mux['role'] == 'logic':
        return int(point)
    try:
        numeric = int(point, 10)
        return numeric
    except ValueError:
        return ord(point) - ord('A') + 1

def get_nets(ctx, gateway):
    session = ctx.obj.session
    resp = session.all_muxes(gateway)
    resp.raise_for_status()
    return resp.json()['muxes']


def display_nets(muxes, netname, net_role=None):
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 't'])
    table.set_cols_align(['l', 'r', 'r'])
    table.add_row(['name', 'type', 'channel'])
    for mux in muxes:
        for mapping in mux['mappings']:
            if netname is None or netname == mapping['net']:
                channel = channel_num(mux, mapping)
                if net_role!=None:
                    if net_role == mux['role']:
                        table.add_row([mapping['net'], mux['role'], channel])
                else:
                    table.add_row([mapping['net'], mux['role'], channel])

    click.echo(table.draw())

def validate_net(ctx, gateway, netname, net_role):
    muxes = get_nets(ctx, gateway)
    for mux in muxes:
        for mapping in mux['mappings']:
            if netname == mapping['net']:
                if net_role == mux['role']:
                    return True
    return False 

@click.group(invoke_without_command=True)
@click.argument('NETNAME', required=False)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
def logic(ctx, gateway, dut, netname):
    """
        Interface for logic nets
    """
    gateway = gateway or dut
    if netname!=None:
        ctx.obj.netname = netname
    if ctx.invoked_subcommand is not None:
        return

    if gateway is None:
        gateway = get_default_gateway(ctx)

    muxes = get_nets(ctx, gateway)

    display_nets(muxes, None, 'logic')    


@logic.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def disable(ctx, gateway, dut, mcu):
    """
        Disable Net
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'disable_net',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('enable_disable.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@logic.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def enable(ctx, gateway, dut, mcu):
    """
        Enable Net
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return    

    data = {
        'action': 'enable_net',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('enable_disable.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@logic.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def start(ctx, gateway, dut, mcu):
    """
        Start waveform capture
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return    

    data = {
        'action': 'start_capture',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('enable_disable.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@logic.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def start_single(ctx, gateway, dut, mcu):
    """
        Start a single waveform capture
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'start_single',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('enable_disable.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@logic.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def stop(ctx, gateway, dut, mcu):
    """
        Stop waveform capture
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'stop_capture',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('enable_disable.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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


@logic.group()
def measure():
    """
        Measure characteristics of logic nets
    """    
    pass

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def period(ctx, mcu, gateway, dut, display, cursor):
    """
    Measure period of captured net waveform
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return    

    data = {
        'action': 'measure_period',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'display': display,
            'cursor': cursor            
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('measurement.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def freq(ctx, mcu, gateway, dut, display, cursor):
    """
    Measure frequency of captured net waveform
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'measure_freq',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'display': display,
            'cursor': cursor            
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('measurement.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def dc_pos(ctx, mcu, gateway, dut, display, cursor):
    """
    Measure positive duty cycle
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'measure_dc_pos',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'display': display,
            'cursor': cursor            
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('measurement.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def dc_neg(ctx, mcu, gateway, dut, display, cursor):
    """
    Measure negative duty cycle
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'measure_dc_neg',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'display': display,
            'cursor': cursor            
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('measurement.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def pw_pos(ctx, mcu, gateway, dut, display, cursor):
    """
    Measure positive pulse width
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'measure_pw_pos',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'display': display,
            'cursor': cursor            
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('measurement.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@measure.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--display', default=False, type=click.BOOL, help='Display measurement on screen')
@click.option('--cursor', default=False, type=click.BOOL, help='Enable measurement cursor')
def pw_neg(ctx, mcu, gateway, dut, display, cursor):
    """
    Measure negative pulse width
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'measure_dc_pos',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'display': display,
            'cursor': cursor            
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('measurement.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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


@logic.group()
def trigger():
    """
        Set up trigger properties for logic nets
    """    
    pass


MODE_CHOICES = click.Choice(('normal', 'auto', 'single'))
COUPLING_CHOICES = click.Choice(('dc', 'ac', 'low_freq_rej', 'high_freq_rej'))

@trigger.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source', required=False, help='Trigger source', metavar='NET')
@click.option('--slope', type=click.Choice(('rising', 'falling', 'both')), help='Trigger slope')
@click.option('--level', type=click.FLOAT, help='Trigger level')
def edge(ctx, mcu, gateway, dut, mode, coupling, source, slope, level):
    """
    Set edge trigger
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'trigger_edge',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'mode': mode,
            'coupling': coupling,
            'source': source,
            'slope': slope,
            'level': level,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('trigger.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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


@trigger.command()
@click.pass_context
@click.option('--mcu', required=False)
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source', required=False, help='Trigger source', metavar='NET')
@click.option('--level', type=click.FLOAT, help='Trigger level')
@click.option('--trigger-on', type=click.Choice(('gt', 'lt', 'gtlt')), help='Trigger on')
@click.option('--upper', type=click.FLOAT, help='upper width')
@click.option('--lower', type=click.FLOAT, help='lower width')
def pulse(ctx, mcu, gateway, dut, mode, coupling, source, level, trigger_on, upper, lower):
    """
    Set pulse trigger
    """

    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'trigger_pulse',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'mode': mode,
            'coupling': coupling,
            'source': source,
            'level': level,
            'trigger_on': trigger_on,
            'upper': upper,
            'lower': lower,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('trigger.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@trigger.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode, e.g. Normal, Automatic, or Single Shot', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source-scl', required=False, help='Trigger source', metavar='NET')
@click.option('--source-sda', required=False, help='Trigger source', metavar='NET')
@click.option('--level-scl', type=click.FLOAT, help='Trigger scl level')
@click.option('--level-sda', type=click.FLOAT, help='Trigger sda level')
@click.option('--trigger-on', type=click.Choice(('start', 'restart', 'stop', 'nack', 'address', 'data', 'addr_data')), help='Trigger on')
@click.option('--address', type=click.INT, help='Address value to trigger on in ADDRESS mode')
@click.option('--addr-width', type=click.Choice(('7', '8', '9', '10')), help='Address width in bits')
@click.option('--data', type=click.INT, help='Data value to trigger on in DATA mode')
@click.option('--data-width', type=click.Choice(('1', '2', '3', '4', '5')), help='Data width in bytes')
@click.option('--direction', type=click.Choice(('write', 'read', 'rw')), help='Direction to trigger on')
def i2c(ctx, gateway, dut, mcu, mode, coupling, source_scl, level_scl, source_sda, level_sda, trigger_on, address, addr_width, data, data_width, direction):
    """
    Set I2C trigger
    """
    if addr_width !=None:
        addr_width = int(addr_width)
    if data_width !=None:
        data_width = int(data_width)
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'trigger_i2c',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'mode': mode,
            'coupling': coupling,
            'source_scl': source_scl,
            'source_sda': source_sda,
            'level_scl': level_scl,
            'level_sda': level_sda,
            'trigger_on': trigger_on,
            'address': address,
            'addr_width': addr_width,
            'data': data,
            'data_width': data_width,
            'direction': direction
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('trigger.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@trigger.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode, e.g. Normal, Automatic, or Single Shot', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source', required=False, help='Trigger source', metavar='NET')
@click.option('--level', type=click.FLOAT, help='Trigger level')
@click.option('--trigger-on', type=click.Choice(('start', 'error', 'cerror', 'data')), help='Trigger on')
@click.option('--parity', type=click.Choice(('even', 'odd', 'none')), help='Data trigger parity')
@click.option('--stop-bits', type=click.Choice(('1', '1.5', '2')), help='Data trigger stop bits')
@click.option('--baud', type=click.INT, help='Data trigger baud')
@click.option('--data-width', type=click.INT, help='Data trigger data width in bits')
@click.option('--data', type=click.INT, help='Data trigger data')
def uart(ctx, gateway, dut, mcu, mode, coupling, source, level, trigger_on, parity, stop_bits, baud, data_width, data):
    """
    Set UART trigger
    """
    if stop_bits !=None:
        stop_bits = float(stop_bits)
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'trigger_uart',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'mode': mode,
            'coupling': coupling,
            'source': source,
            'level': level,
            'trigger_on': trigger_on,
            'parity': parity,
            'stop_bits': stop_bits,
            'baud': baud,
            'data_width': data_width,
            'data': data,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('trigger.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@trigger.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--mode', default='normal', type=MODE_CHOICES, help='Trigger mode, e.g. Normal, Automatic, or Single Shot', show_default=True)
@click.option('--coupling', default='dc', type=COUPLING_CHOICES, help='Coupling mode', show_default=True)
@click.option('--source-mosi-miso', required=False, help='Trigger master/slave data source', metavar='NET')
@click.option('--source-sck', required=False, help='Trigger clock source', metavar='NET')
@click.option('--source-cs', required=False, help='Trigger chip select source', metavar='NET')
@click.option('--level-mosi-miso', type=click.FLOAT, help='Trigger mosi/miso level')
@click.option('--level-sck', type=click.FLOAT, help='Trigger sck level')
@click.option('--level-cs', type=click.FLOAT, help='Trigger cs level')
@click.option('--data', type=click.INT, help='Trigger data value')
@click.option('--data-width', type=click.INT, help='Data width in bits')
@click.option('--clk-slope', type=click.Choice(('positive', 'negative')), help='Slope of clock edge to sample data')
@click.option('--trigger-on', type=click.Choice(('timeout', 'cs')), help='Trigger on')
@click.option('--cs-idle', type=click.Choice(('high', 'low')), help='CS Idle type')
@click.option('--timeout', type=click.FLOAT, help='Timeout length')
def spi(ctx, gateway, dut, mcu, mode, coupling, source_mosi_miso, source_sck, source_cs, level_mosi_miso, level_sck, level_cs, data, data_width, clk_slope, trigger_on, cs_idle, timeout):
    """
    Set SPI trigger
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'trigger_spi',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'mode': mode,
            'coupling': coupling,
            'source_mosi_miso': source_mosi_miso,
            'source_sck': source_sck,
            'source_cs': source_cs,
            'level_mosi_miso': level_mosi_miso,
            'level_sck': level_sck,
            'level_cs': level_cs,
            'data': data,
            'data_width': data_width,
            'clk_slope': clk_slope,
            'trigger_on': trigger_on,            
            'cs_idle': cs_idle,
            'timeout': timeout
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('trigger.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@logic.group()
def cursor():
    """
        Move scope cursor on a given net
    """    
    pass

@cursor.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--x', required=False, type=click.FLOAT, help='cursor a x coordinate')
@click.option('--y', required=False, type=click.FLOAT, help='cursor a y coordinate')
def set_a(ctx, gateway, dut, mcu, x, y):
    """
        Set cursor a's x position
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'set_a',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'x': x,
            'y': y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('cursor.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@cursor.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--x', required=False, type=click.FLOAT, help='cursor b x coordinate')
@click.option('--y', required=False, type=click.FLOAT, help='cursor b y coordinate')
def set_b(ctx, gateway, dut, mcu, x, y):
    """
        Set cursor b's x position
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'set_b',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'x': x,
            'y': y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('cursor.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@cursor.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--del-x', required=False, type=click.FLOAT, help='shift a\'s x coordinate')
@click.option('--del-y', required=False, type=click.FLOAT, help='shift a\'s y coordinate')
def move_a(ctx, gateway, dut, mcu, del_x, del_y):
    """
        Shift cursor a's  position
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'move_a',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'del_x': del_x,
            'del_y': del_y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('cursor.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@cursor.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--del-x', required=False, type=click.FLOAT, help='shift b\'s x coordinate')
@click.option('--del-y', required=False, type=click.FLOAT, help='shift b\'s y coordinate')
def move_b(ctx, gateway, dut, mcu, del_x, del_y):
    """
        Shift cursor b's position
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'move_b',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'del_x': del_x,
            'del_y': del_y,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('cursor.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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

@cursor.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def hide(ctx, gateway, dut, mcu):
    """
        Hide cursor
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'logic') is False:
        print(f"{netname} is not a logic net")
        return

    data = {
        'action': 'hide_cursor',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('cursor.py'),
        dut,
        image='',
        env=(f'LAGER_COMMAND_DATA={json.dumps(data)}',),
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