"""
    Supply commands
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
def supply(ctx, gateway, dut, netname):
    """
        Interface for supply nets
    """
    gateway = gateway or dut
    if netname!=None:
        ctx.obj.netname = netname
    if ctx.invoked_subcommand is not None:
        return

    if gateway is None:
        gateway = get_default_gateway(ctx)

    muxes = get_nets(ctx, gateway)
    display_nets(muxes, None, 'power-supply')   



@supply.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--ocp', required=False, type=click.FLOAT, help='Set over current protection')
@click.option('--ovp', required=False, type=click.FLOAT, help='Set over voltage protection')
@click.option('--yes', is_flag=True, default=False)
def voltage(ctx, gateway, dut, mcu, value, ocp, ovp, yes):
    """
        Set voltage for net
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
        return

    if value != None:
        try:
            float(value)
        except ValueError:
            print(f"{value} is not a number") 
            return

        if yes or click.confirm(f"Set voltage to {value}V?", default=False):
            pass
        else:
            print("Aborting")
            return

    data = {
        'action': 'voltage',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
            'ocp': ocp,
            'ovp': ovp,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('supply.py'),
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

@supply.command()
@click.argument('VALUE', required=False, type=click.FLOAT)
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--ocp', required=False, type=click.FLOAT, help='Set over current protection')
@click.option('--ovp', required=False, type=click.FLOAT, help='Set over voltage protection')
@click.option('--yes', is_flag=True, default=False)
def current(ctx, gateway, dut, mcu, value, ocp, ovp, yes):
    """
        Set current on net
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
        return

    if value != None:
        try:
            float(value)
        except ValueError:
            print(f"{value} is not a number")

        if yes or click.confirm(f"Set current to {value}A?", default=False):
            pass
        else:
            print("Aborting")
            return

    data = {
        'action': 'current',
        'mcu': mcu,
        'params': {
            'netname': netname,
            'value': value,
            'ocp': ocp,
            'ovp': ovp,
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('supply.py'),
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

@supply.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.confirmation_option(prompt='Disable Net?')
def disable(ctx, gateway, dut, mcu):
    """
        Disable Supply
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
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
        get_impl_path('supply.py'),
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

@supply.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.confirmation_option(prompt='Enable Net?')
def enable(ctx, gateway, dut, mcu):
    """
        Enable Supply
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
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
        get_impl_path('supply.py'),
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


@supply.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def state(ctx, gateway, dut, mcu):
    """
        Get power state of net
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
        return

    data = {
        'action': 'get_state',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('supply.py'),
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

@supply.command(name='set')
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def set_mode(ctx, gateway, dut, mcu):
    """
        Set power supply mode
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
        return

    data = {
        'action': 'set_mode',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('supply.py'),
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


@supply.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def clear_ovp(ctx, gateway, dut, mcu):
    """
        Clear OVP
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
        return

    data = {
        'action': 'clear_ovp',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('supply.py'),
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

@supply.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
def clear_ocp(ctx, gateway, dut, mcu):
    """
        Clear OCP
    """
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    netname = ctx.obj.netname

    if validate_net(ctx, gateway, netname, 'power-supply') is False:
        print(f"{netname} is not a supply net")
        return

    data = {
        'action': 'clear_ocp',
        'mcu': mcu,
        'params': {
            'netname': netname,
        }
    }
    run_python_internal(
        ctx,
        get_impl_path('supply.py'),
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