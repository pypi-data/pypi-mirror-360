"""
    List Nets
"""
import json
import click
from texttable import Texttable
from ..context import get_default_gateway
from ..context import get_impl_path
from ..python.commands import run_python_internal

def is_int(val):
    try:
        int(val)
    except:
        return False
    return True

def channel_num(mux, mapping):
    point = mux['scope_points'][0][1]
    if mux['role'] == 'analog':
        return ord(point) - ord('A') + 1
    if mux['role'] == 'logic':
        return int(point)
    if mux['role'] == 'gpio':
        if is_int(point):
            return f'FIO{point}'
        return point
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

@click.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
def nets(ctx, gateway, dut):
    """
        List all nets
    """
    gateway = gateway or dut


    if gateway is None:
        gateway = get_default_gateway(ctx)

    muxes = get_nets(ctx, gateway)
    display_nets(muxes, None, None)


@click.command()
@click.pass_context
@click.option('--dut', help='ID of DUT')
@click.option('--name', help='Device Name', required=True, hidden=True)
@click.option('--vid', help='Device VID', required=True, hidden=True)
@click.option('--pid', help='Device PID', required=True, hidden=True)
@click.option('--serial', help='Device Serial', required=False, hidden=True)
@click.option('--other', help='Device Serial', required=False, hidden=True)
def create_instrument(ctx, dut, name, vid, pid, serial, other):
    """
        Create an instrument
    """
    if dut is None:
        dut = get_default_gateway(ctx)

    session = ctx.obj.session
    data = {
        'name': name,
        'vid': vid,
        'pid': pid,
        'serial': serial,
        'other': other,
    }
    resp = session.create_instrument(dut, data)
    resp.raise_for_status()
    print(resp.json())

@click.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
def probe_instruments(ctx, dut):
    """
        Probe instruments on dut
    """    
    if dut is None:
        dut = get_default_gateway(ctx)

    run_python_internal(
        ctx,
        get_impl_path('probe_instruments.py'),
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


@click.command()
@click.pass_context
@click.option('--dut', help='ID of DUT')
def list_instruments(ctx, dut):
    """
        List instruments
    """
    if dut is None:
        dut = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.list_instruments(dut)
    resp.raise_for_status()
    print(resp.json())
