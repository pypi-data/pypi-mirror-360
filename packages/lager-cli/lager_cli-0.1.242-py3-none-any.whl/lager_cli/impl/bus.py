import os
import json
import time
from lager.pcb.net import Net, NetType
from lager.pcb.bus import I2C, UART, SPI, CAN

def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass

def bus_uart(source_tx, source_rx, level_tx, level_rx, parity, stop_bits, data_bits, baud, polarity, endianness, packet_ending, disable):
    tx = Net(source_tx, type=None, setup_function=net_setup, teardown_function=net_teardown)
    rx = Net(source_rx, type=None, setup_function=net_setup, teardown_function=net_teardown)
    uart = UART(tx=tx,rx=rx)
    if disable==True:
        uart.disable()
        return

    uart.set_signal_threshold(tx=level_tx,rx=level_rx)
    if parity!=None:
        if parity.lower() == 'none':
            uart.set_parity_none()
        elif parity.lower() == 'even':
            uart.set_parity_even()
        elif parity.lower() == 'odd':
            uart.set_parity_odd() 
        else:
            raise ValueError(f"{parity} is not a valid option")           

    if stop_bits!=None:
        if stop_bits == 1 or stop_bits == 2:
            stop_bits = int(stop_bits)
        uart.set_stop_bits(stop_bits)

    if data_bits!=None:
        uart.set_data_bits(data_bits)

    if baud!=None:
        uart.set_baud(baud)

    if polarity!=None:
        if polarity.lower() == 'pos':
            uart.set_polarity_positive()
        elif polarity.lower() == 'neg':
            uart.set_polarity_negative()
        else:
            raise ValueError(f"{polarity} is not a valid option")

    if endianness!=None:
        if endianness.lower() == 'msb':
            uart.set_endianness_msb()
        elif endianness.lower() == 'lsb':
            uart.set_endianness_lsb()
        else:
            raise ValueError(f"{endianness} is not a valid option")

    if packet_ending!=None:
        if packet_ending.lower() == 'null':
            uart.set_packet_ending_null()
        elif packet_ending.lower() == 'lf':
            uart.set_packet_ending_lf()
        elif packet_ending.lower() == 'cr':
            uart.set_packet_ending_cr()
        elif packet_ending.lower() == 'sp':
            uart.set_packet_ending_space()
        elif packet_ending.lower() == 'none':
            uart.disable_packet_ending()                                    
        else:
            raise ValueError(f"{packet_ending} is not a valid option")

    uart.enable()                    

def bus_i2c(source_scl, source_sda, level_scl, level_sda, rw, disable):
    scl = Net(source_scl, type=None, setup_function=net_setup, teardown_function=net_teardown)
    sda = Net(source_sda, type=None, setup_function=net_setup, teardown_function=net_teardown)
    i2c = I2C(scl=scl,sda=sda)
    if disable==True:
        i2c.disable()
        return

    i2c.set_signal_threshold(sda=level_sda,scl=level_scl)
    if rw!=None:
        if rw.lower() == 'on':
            i2c.rw_on()
        elif rw.lower() == 'off':
            i2c.rw_off()
        else:
            raise ValueError(f"{rw} is not a valid option")

    i2c.enable()

def bus_spi(source_mosi, source_miso, source_sck, source_cs, level_mosi, level_miso, level_sck, level_cs, pol_mosi, pol_miso, pol_cs, pha_sck, capture, timeout, endianness, data_width, disable):
    mosi = Net(source_mosi, type=None, setup_function=net_setup, teardown_function=net_teardown)
    miso = Net(source_miso, type=None, setup_function=net_setup, teardown_function=net_teardown)
    sck = Net(source_sck, type=None, setup_function=net_setup, teardown_function=net_teardown)
    cs = None
    if source_cs!=None:
        cs = Net(source_cs, type=None, setup_function=net_setup, teardown_function=net_teardown)    

    spi = SPI(clk=sck, mosi=mosi, miso=miso, cs=cs)
    if disable==True:
        spi.disable()
        return 

    if capture!=None:
        if capture.lower() == 'timeout':
            spi.set_capture_mode_timeout(None)
            if timeout!=None:
                spi.set_capture_mode_timeout(timeout)
        elif capture.lower() == 'cs':
            spi.set_capture_mode_cs()

    if pol_cs!=None:
        if pol_cs.lower() == 'pos':
            pol_cs = 1
        elif pol_cs.lower() == 'neg':
            pol_cs = 0
        else:
            raise ValueError(f"{pol_cs} is not a valid option")

    if pol_mosi!=None:
        if pol_mosi.lower() == 'pos':
            pol_mosi = 1
        elif pol_mosi.lower() == 'neg':
            pol_mosi = 0
        else:
            raise ValueError(f"{pol_mosi} is not a valid option")

    if pol_miso!=None:
        if pol_miso.lower() == 'pos':
            pol_miso = 1
        elif pol_miso.lower() == 'neg':
            pol_miso = 0
        else:
            raise ValueError(f"{pol_miso} is not a valid option")                                

    spi.set_signal_polarity(mosi=pol_mosi, miso=pol_miso, cs=pol_cs)

    if pha_sck!=None:
        if pha_sck.lower() == 'rising':
            spi.set_sck_phase_rising_edge()
        elif pha_sck.lower() == 'falling':
            spi.set_sck_phase_falling_edge()

    spi.set_signal_threshold(mosi=level_mosi, miso=level_miso, sck=level_sck, cs=level_cs)

    if endianness!=None:
        if endianness.lower() == 'msb':
            spi.set_endianness_msb()
        elif endianness.lower() == 'lsb':
            spi.set_endianness_lsb()
        else:
            raise ValueError(f"{endianness} is not a valid option")                  

    if data_width!=None:
        spi.set_data_width(data_width)
        
    spi.enable()

def bus_can(source, level, baud, signal_type, disable):
    sig = Net(source, type=None, setup_function=net_setup, teardown_function=net_teardown)    
    can = CAN(can=sig)
    if disable==True:
        can.disable()
        return
    
    if level!=None:
        can.set_threshold(level)
    if baud!=None:
        can.set_baud(baud)
    if signal_type!=None:
        if signal_type.lower() == 'tx':
            can.set_signal_type_tx()
        elif signal_type.lower() == 'rx':
            can.set_signal_type_rx()
        elif signal_type.lower() == 'can_h':
            can.set_signal_type_can_high()  
        elif signal_type.lower() == 'can_l':
            can.set_signal_type_can_low()  
        elif signal_type.lower() == 'diff':
            can.set_signal_type_can_differential()
        else:
            raise ValueError(f"{signal_type} is not a valid option")

    can.enable()

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] == 'bus_uart':
        bus_uart(**command['params'])
    elif command['action'] == 'bus_i2c':
        bus_i2c(**command['params'])
    elif command['action'] == 'bus_spi':
        bus_spi(**command['params'])
    elif command['action'] == 'bus_can':
        bus_can(**command['params'])                 
    else:
        pass

if __name__ == '__main__':
    main()