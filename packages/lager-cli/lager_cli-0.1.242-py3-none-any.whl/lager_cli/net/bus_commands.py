"""
    Bus commands
"""
import json
import click
from texttable import Texttable
from ..context import get_default_gateway
from ..context import get_impl_path
from ..python.commands import run_python_internal

@click.group()
def bus():
    """
        Interface for Communication Busses
    """    
    pass


@bus.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--source-tx', required=True, help='UART Bus TX signal', metavar='NET')
@click.option('--source-rx', required=True, help='UART Bus RX signal', metavar='NET')
@click.option('--level-tx', required=False, type=click.FLOAT, help='tx signal threshold level')
@click.option('--level-rx', required=False, type=click.FLOAT, help='rx signal threshold level')
@click.option('--parity', required=False, type=click.Choice(('even', 'odd', 'none')), help='Bus parity')
@click.option('--stop-bits', required=False, type=click.Choice(('1', '1.5', '2')), help='Bus stop bits')
@click.option('--data-bits', required=False, type=click.Choice(('5', '6', '7','8','9')), help='Bus stop bits')
@click.option('--baud', required=False, type=click.INT, help='Bus baud')
@click.option('--polarity', required=False, type=click.Choice(('pos', 'neg')), help='Bus polarity. Typical is negative')
@click.option('--endianness', required=False, type=click.Choice(('msb', 'lsb')), help='Bus endianness')
@click.option('--packet-ending', required=False, type=click.Choice(('null', 'cr', 'lf', 'sp', 'none')), help='Packet Ending of data')
@click.option('--disable', is_flag=True)
def uart(ctx, gateway, dut, mcu, source_tx, source_rx, level_tx, level_rx, parity, stop_bits, data_bits, baud, polarity, endianness, packet_ending, disable):
    """
        Enable UART Bus Decoding
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)
    if stop_bits != None:
        stop_bits = float(stop_bits)

    if data_bits != None:
        data_bits = int(data_bits)
    data = {
        'action': 'bus_uart',
        'mcu': mcu,
        'params': {
            'source_tx': source_tx,
            'source_rx': source_rx,
            'level_tx': level_tx,
            'level_rx': level_rx,
            'parity': parity,
            'stop_bits': stop_bits,
            'data_bits': data_bits,
            'baud': baud,
            'polarity': polarity,
            'endianness': endianness,
            'packet_ending': packet_ending,
            'disable': disable
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('bus.py'),
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

@bus.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--source-scl', required=True, help='I2C Bus SCL signal', metavar='NET')
@click.option('--source-sda', required=True, help='I2C Bus SDA signal', metavar='NET')
@click.option('--level-scl', required=False, type=click.FLOAT, help='scl signal threshold level')
@click.option('--level-sda', required=False, type=click.FLOAT, help='sda signal threshold level')
@click.option('--rw', required=False, type=click.Choice(('on', 'off')), help='Decode RW bit')
@click.option('--disable', is_flag=True)
def i2c(ctx, gateway, dut, mcu, source_scl, source_sda, level_scl, level_sda, rw, disable):
    """
        Enable I2C Bus Decoding
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    data = {
        'action': 'bus_i2c',
        'mcu': mcu,
        'params': {
            'source_scl': source_scl,
            'source_sda': source_sda,
            'level_scl': level_scl,
            'level_sda': level_sda,
            'rw': rw,
            'disable': disable
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('bus.py'),
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

@bus.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--source-mosi', required=True, help='SPI Bus MOSI signal', metavar='NET')
@click.option('--source-miso', required=True, help='SPI Bus MISO signal', metavar='NET')
@click.option('--source-sck', required=True, help='SPI Bus SCK signal', metavar='NET')
@click.option('--source-cs', required=False, help='SPI Bus CS signal', metavar='NET')
@click.option('--level-mosi', required=False, type=click.FLOAT, help='MOSI signal threshold level')
@click.option('--level-miso', required=False, type=click.FLOAT, help='MISO signal threshold level')
@click.option('--level-sck', required=False, type=click.FLOAT, help='SCK signal threshold level')
@click.option('--level-cs', required=False, type=click.FLOAT, help='CS signal threshold level')
@click.option('--pol-mosi', required=False, type=click.Choice(('pos', 'neg')), help='MOSI signal polarity')
@click.option('--pol-miso', required=False, type=click.Choice(('pos', 'neg')), help='MISO signal polarity')
@click.option('--pol-cs', required=False, type=click.Choice(('pos', 'neg')), help='CS signal polarity')
@click.option('--pha-sck', required=False, type=click.Choice(('rising', 'falling')), help='SCK edge to sample data on')
@click.option('--capture', required=False, type=click.Choice(('timeout', 'cs')), help='Mode to capture bus data')
@click.option('--timeout', required=False, type=click.FLOAT, help='Timeout value')
@click.option('--endianness', required=False, type=click.Choice(('msb', 'lsb')), help='Endianness of data')
@click.option('--data-width', required=False, type=click.INT, help='Width in bits of data')
@click.option('--disable', is_flag=True)
def spi(ctx, gateway, dut, mcu, source_mosi, source_miso, source_sck, source_cs, level_mosi, level_miso, level_sck, level_cs, pol_mosi, pol_miso, pol_cs, pha_sck, capture, timeout, endianness, data_width, disable):
    """
        Enable SPI Bus Decoding
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    data = {
        'action': 'bus_spi',
        'mcu': mcu,
        'params': {
            'source_mosi': source_mosi,
            'source_miso': source_miso,
            'source_sck': source_sck,
            'source_cs': source_cs,            
            'level_mosi': level_mosi,
            'level_miso': level_miso,
            'level_mosi': level_mosi,
            'level_miso': level_miso,
            'level_sck': level_sck,
            'level_cs': level_cs,                        
            'pol_mosi': pol_mosi,
            'pol_miso': pol_miso,
            'pol_cs': pol_cs,
            'pha_sck': pha_sck,
            'capture': capture,
            'timeout': timeout,
            'endianness': endianness,
            'data_width': data_width,
            'disable': disable
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('bus.py'),
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

@bus.command()
@click.pass_context
@click.option('--gateway', required=False, help='ID of gateway to which DUT is connected', hidden=True)
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--mcu', required=False)
@click.option('--source', required=True, help='CAN Bus signal', metavar='NET')
@click.option('--level', required=False, type=click.FLOAT, help='signal threshold level')
@click.option('--baud', required=False, type=click.INT, help='Bus BAUD ratae')
@click.option('--signal-type', required=False, type=click.Choice(('tx', 'rx', 'can_h', 'can_l', 'diff')), help='Signal type of source data. e.g tx transceiver, raw CAN high signal, raw CAN low signal, raw differential signal')
@click.option('--disable', is_flag=True)
def can(ctx, gateway, dut, mcu, source, level, baud, signal_type, disable):
    """
        Enable CAN Bus Decoding
    """    
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    data = {
        'action': 'bus_can',
        'mcu': mcu,
        'params': {
            'source': source,
            'level': level,
            'baud': baud,
            'signal_type': signal_type,
            'disable': disable
        }
    }

    run_python_internal(
        ctx,
        get_impl_path('bus.py'),
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