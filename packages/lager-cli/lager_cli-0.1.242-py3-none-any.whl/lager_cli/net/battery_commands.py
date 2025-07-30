"""
    Battery commands
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
def battery(ctx, gateway, dut, netname):
    """
        Interface for battery nets
    """
    gateway = gateway or dut
    if netname!=None:
        ctx.obj.netname = netname
    if ctx.invoked_subcommand is not None:
        return

    if gateway is None:
        gateway = get_default_gateway(ctx)

    muxes = get_nets(ctx, gateway)
    display_nets(muxes, None, 'battery')   

@battery.command()
@click.argument('MODE_TYPE', required=False, type=click.Choice(('static', 'dynamic')))
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def mode(ctx, gateway, dut, mcu, mode_type):
    """
        Set battery simulation mode type
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_mode',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'mode_type': mode_type,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command(name='set')
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def set_mode(ctx, gateway, dut, mcu):
    """
        Set battery mode
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_to_battery_mode',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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



@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def soc(ctx, gateway, dut, mcu, value):
    """
        Set battery state of charge in %
    """   
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_soc',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def voc(ctx, gateway, dut, mcu, value):
    """
        Set battery open circuit voltage in Volts
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_voc',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def batt_full(ctx, gateway, dut, mcu, value):
    """
        Set battery fully charged voltage in Volts
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_volt_full',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def batt_empty(ctx, gateway, dut, mcu, value):
    """
        Set battery fully discharged voltage in Volts
    """      
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_volt_empty',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def capacity(ctx, gateway, dut, mcu, value):
    """
        Set battery capacity limit in Amps-hours
    """      
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_capacity',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def current_limit(ctx, gateway, dut, mcu, value):
    """
        Set maximum charge/discharge current in Amps
    """       
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_current_limit',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def ovp(ctx, gateway, dut, mcu, value):
    """
        Set over voltage protection limit in Volts
    """   
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_ovp',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def ocp(ctx, gateway, dut, mcu, value):
    """
        Set over current protection limit in Amps
    """     
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_ocp',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.argument('PARTNUMBER', required=False)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def model(ctx, gateway, dut, mcu, partnumber):
    """
        Set Battery Model
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'set_model',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'partnumber': partnumber,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def state(ctx, gateway, dut, mcu):
    """
        Get Battery State
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'state',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--yes', is_flag=True, default=False)
def enable(ctx, gateway, dut, mcu, yes):
    """
        Enable Battery
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    if yes or click.confirm(f"Enable Net?", default=False):
        pass
    else:
        print("Aborting")
        return

    data = {
        'action': 'enable_battery',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--yes', is_flag=True, default=False)
def disable(ctx, gateway, dut, mcu, yes):
    """
        Disable Battery
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    if yes or click.confirm(f"Disable Net?", default=True):
        pass
    else:
        print("Aborting")
        return

    data = {
        'action': 'disable_battery',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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

@battery.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def clear_ovp(ctx, gateway, dut, mcu):
    """
        Clear OVP
    """
    do_clear(ctx, gateway, dut, mcu)

@battery.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def clear_ocp(ctx, gateway, dut, mcu):
    """
        Clear OCP
    """
    do_clear(ctx, gateway, dut, mcu)

def do_clear(ctx, gateway, dut, mcu):
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'battery') is False:
        print(f"{netname} is not a battery net")
        return

    data = {
        'action': 'clear',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('battery.py'),
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
