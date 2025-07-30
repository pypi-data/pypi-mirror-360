import os
import json
from lager.pcb.net import Net, NetType, TriggerType,TriggerUARTParity,TriggerI2CDirection

def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass
                                                              
                                                                                                                   

def trigger_uart(netname, mode, coupling, source, level, trigger_on, parity, stop_bits, baud, data_width, data):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.enable()   
    source_net = None
    if source != None:    
        source_net = Net(source, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_net.enable()

    if mode.lower() == "auto":
        target_net.trigger_settings.set_mode_auto()
    elif mode.lower() == "normal":
        target_net.trigger_settings.set_mode_normal()
    elif mode.lower() == "single":
        target_net.trigger_settings.set_mode_single()
    else:
        raise Exception(f"{mode} is not a valid option")

    if coupling.lower() == "dc":
        target_net.trigger_settings.set_coupling_DC()
    elif coupling.lower() == "ac":
        target_net.trigger_settings.set_coupling_AC()
    elif coupling.lower() == "hp_filt":
        target_net.trigger_settings.set_coupling_low_freq_reject()
    elif coupling.lower() == "lp_filt":
        target_net.trigger_settings.set_coupling_high_freq_reject()
    else:
        raise Exception(f"{coupling} type is not a valid option")

    target_net.trigger_settings.set_type(TriggerType.UART)

    if source_net != None:
        target_net.trigger_settings.uart.set_source(source_net)

    if level != None:
        target_net.trigger_settings.uart.set_level(level)
            
    trig_parity = None
    if parity != None:
        if parity.lower() == "even":
            trig_parity = TriggerUARTParity.Even
        elif parity.lower() == "odd":
            trig_parity = TriggerUARTParity.Odd
        elif parity.lower() == "none":
            trig_parity = TriggerUARTParity.NoParity
        else:
            raise Exception(f"{parity} is not a valid option")        
    target_net.trigger_settings.uart.set_uart_params(parity=trig_parity, stopbits=stop_bits, baud=baud, bits=data_width)

    if trigger_on != None:
        if trigger_on.lower() == "start":
            target_net.trigger_settings.uart.set_trigger_on_start()
        elif trigger_on.lower() == "error":
            target_net.trigger_settings.uart.set_trigger_on_error()
        elif trigger_on.lower() == "cerror":
            target_net.trigger_settings.uart.set_trigger_on_cerror()
        elif trigger_on.lower() == "data":
            target_net.trigger_settings.uart.set_trigger_on_data(data=data)
        else:
            raise Exception(f"{trigger_on} type is not a valid option")        

def trigger_edge(netname, mode, coupling, source, level, slope):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.enable()
    source_net = None
    if source != None:
        source_net = Net(source, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_net.enable()

    if mode.lower() == "auto":
        target_net.trigger_settings.set_mode_auto()
    elif mode.lower() == "normal":
        target_net.trigger_settings.set_mode_normal()
    elif mode.lower() == "single":
        target_net.trigger_settings.set_mode_single()
    else:
        raise Exception(f"{mode} is not a valid option")

    if coupling.lower() == "dc":
        target_net.trigger_settings.set_coupling_DC()
    elif coupling.lower() == "ac":
        target_net.trigger_settings.set_coupling_AC()
    elif coupling.lower() == "hp_filt":
        target_net.trigger_settings.set_coupling_low_freq_reject()
    elif coupling.lower() == "lp_filt":
        target_net.trigger_settings.set_coupling_high_freq_reject()
    else:
        raise Exception(f"{coupling} is not a valid option")

    target_net.trigger_settings.set_type(TriggerType.Edge)
    if source_net != None:
        target_net.trigger_settings.edge.set_source(source_net)

    if level != None:
        target_net.trigger_settings.edge.set_level(level)
    if slope != None:
        if slope.lower() == "rising":
            target_net.trigger_settings.edge.set_slope_rising()
        elif slope.lower() == "falling":
            target_net.trigger_settings.edge.set_slope_falling()
        elif slope.lower() == "both":
            target_net.trigger_settings.edge.set_slope_both()
        else:
            raise Exception(f"{slope} is not a valid option")

def trigger_pulse(netname, mode, coupling, source, level, trigger_on, upper, lower):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.enable()

    source_net = None
    if source != None:    
        source_net = Net(source, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_net.enable()

    if mode.lower() == "auto":
        target_net.trigger_settings.set_mode_auto()
    elif mode.lower() == "normal":
        target_net.trigger_settings.set_mode_normal()
    elif mode.lower() == "single":
        target_net.trigger_settings.set_mode_single()
    else:
        raise Exception(f"{mode} is not a valid option")

    if coupling.lower() == "dc":
        target_net.trigger_settings.set_coupling_DC()
    elif coupling.lower() == "ac":
        target_net.trigger_settings.set_coupling_AC()
    elif coupling.lower() == "hp_filt":
        target_net.trigger_settings.set_coupling_low_freq_reject()
    elif coupling.lower() == "lp_filt":
        target_net.trigger_settings.set_coupling_high_freq_reject()
    else:
        raise Exception(f"{coupling} is not a valid option")

    target_net.trigger_settings.set_type(TriggerType.Pulse)

    if source_net != None:
        target_net.trigger_settings.pulse.set_source(source_net)

    if level != None:
        target_net.trigger_settings.pulse.set_level(level)

    if trigger_on != None:
        if trigger_on.lower() == "gt":
            target_net.trigger_settings.pulse.set_trigger_on_pulse_greater_than_width(lower)
        elif trigger_on.lower() == "lt":
            target_net.trigger_settings.pulse.set_trigger_on_pulse_less_than_width(upper)
        elif trigger_on.lower() == "gtlt":
            target_net.trigger_settings.pulse.set_trigger_on_pulse_less_than_greater_than(max_pulse_width=upper, min_pulse_width=lower)
        else:
            raise Exception(f"{target_net} is not a valid option")


def trigger_i2c(netname, mode, coupling, source_scl, level_scl, source_sda, level_sda, trigger_on, address, addr_width, data, data_width, direction):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.enable()
    
    source_scl_net = None
    if source_scl != None:
        source_scl_net = Net(source_scl, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_scl_net.enable()    
    
    source_sda_net = None
    if source_sda !=None:
        source_sda_net = Net(source_sda, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_sda_net.enable()

    if mode.lower() == "auto":
        target_net.trigger_settings.set_mode_auto()
    elif mode.lower() == "normal":
        target_net.trigger_settings.set_mode_normal()
    elif mode.lower() == "single":
        target_net.trigger_settings.set_mode_single()
    else:
        raise Exception(f"{mode} is not a valid option")

    if coupling.lower() == "dc":
        target_net.trigger_settings.set_coupling_DC()
    elif coupling.lower() == "ac":
        target_net.trigger_settings.set_coupling_AC()
    elif coupling.lower() == "hp_filt":
        target_net.trigger_settings.set_coupling_low_freq_reject()
    elif coupling.lower() == "lp_filt":
        target_net.trigger_settings.set_coupling_high_freq_reject()
    else:
        raise Exception(f"{coupling} is not a valid option")

    target_net.trigger_settings.set_type(TriggerType.I2C)


    target_net.trigger_settings.i2c.set_source(net_scl=source_scl_net, net_sda=source_sda_net)

    if level_scl != None:
        target_net.trigger_settings.i2c.set_scl_trigger_level(level_scl)

    if level_sda != None:        
        target_net.trigger_settings.i2c.set_sda_trigger_level(level_sda)

    if direction!=None:
        if direction == 'write':
            direction = TriggerI2CDirection.Write
        elif direction == 'read':
            direction = TriggerI2CDirection.Read
        elif direction == 'rw':
            direction = TriggerI2CDirection.RW
        else:
            raise Exception(f"{direction} is not a valid option")

    if trigger_on != None:
        if trigger_on.lower() == "start":
            target_net.trigger_settings.i2c.set_trigger_on_start()
        elif trigger_on.lower() == "restart":
            target_net.trigger_settings.i2c.set_trigger_on_restart()
        elif trigger_on.lower() == "stop":
            target_net.trigger_settings.i2c.set_trigger_on_stop()
        elif trigger_on.lower() == "nack":
            target_net.trigger_settings.i2c.set_trigger_on_nack()  
        elif trigger_on.lower() == "address":
            target_net.trigger_settings.i2c.set_trigger_on_address(bits=addr_width, direction=direction, address=address) 
        elif trigger_on.lower() == "data":
            target_net.trigger_settings.i2c.set_trigger_on_data(width=data_width, data=data)
        elif trigger_on.lower() == "addr_data":
            target_net.trigger_settings.i2c.set_trigger_on_addr_data(bits=addr_width, direction=direction, address=address, width=data_width, data=data)                                
        else:
            raise Exception(f"{trigger_on} is not a valid option")

def trigger_spi(netname, mode, coupling, source_mosi_miso, source_sck, source_cs, level_mosi_miso, level_sck, level_cs, data, data_width, clk_slope, trigger_on, cs_idle, timeout):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.enable()    
    
    source_mosi_miso_net = None
    if source_mosi_miso != None:
        source_mosi_miso_net = Net(source_mosi_miso, type=None, setup_function=net_setup, teardown_function=net_teardown)    
        source_mosi_miso_net.enable()

    source_sck_net = None
    if source_sck != None:
        source_sck_net = Net(source_sck, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_sck_net.enable()
    
    source_cs_net = None
    if source_cs != None:
        source_cs_net = Net(source_cs, type=None, setup_function=net_setup, teardown_function=net_teardown)
        source_cs_net.enable()            

    if mode.lower() == "auto":
        target_net.trigger_settings.set_mode_auto()
    elif mode.lower() == "normal":
        target_net.trigger_settings.set_mode_normal()
    elif mode.lower() == "single":
        target_net.trigger_settings.set_mode_single()
    else:
        raise Exception(f"{mode} is not a valid option")

    if coupling.lower() == "dc":
        target_net.trigger_settings.set_coupling_DC()
    elif coupling.lower() == "ac":
        target_net.trigger_settings.set_coupling_AC()
    elif coupling.lower() == "hp_filt":
        target_net.trigger_settings.set_coupling_low_freq_reject()
    elif coupling.lower() == "lp_filt":
        target_net.trigger_settings.set_coupling_high_freq_reject()
    else:
        raise Exception(f"{coupling} is not a valid option")

    target_net.trigger_settings.set_type(TriggerType.SPI)
    target_net.trigger_settings.spi.set_source(net_sck=source_sck_net, net_mosi_miso=source_mosi_miso_net, net_cs=source_cs_net)
    
    if level_mosi_miso != None:
        target_net.trigger_settings.spi.set_mosi_miso_trigger_level(level_mosi_miso)    
    
    if level_sck != None:
        target_net.trigger_settings.spi.set_sck_trigger_level(level_sck)
    
    if level_cs != None:
        target_net.trigger_settings.spi.set_cs_trigger_level(level_cs)
    
    
    target_net.trigger_settings.spi.set_trigger_data(bits=data_width, data=data)

    if clk_slope != None:
        if clk_slope.lower() == "positive":
            target_net.trigger_settings.spi.set_clk_edge_positive()
        elif clk_slope.lower() == "negative":
            target_net.trigger_settings.spi.set_clk_edge_negative()      

    if trigger_on != None:
        if trigger_on.lower() == "timeout":
            if timeout!=None:
                target_net.trigger_settings.spi.set_trigger_on_timeout(timeout)
        elif trigger_on.lower() == "cs":
            if cs_idle!=None:
                if cs_idle.lower() == "high":
                    target_net.trigger_settings.spi.set_trigger_on_cs_low()
                elif cs_idle.lower() == "low":
                    target_net.trigger_settings.spi.set_trigger_on_cs_high()
                else:
                    raise Exception(f"{cs_idle} is not a valid option")
        else:
            raise Exception(f"{trigger_on} is not a valid option")

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] == 'trigger_uart':
        trigger_uart(**command['params'])
    elif command['action'] == 'trigger_edge':
        trigger_edge(**command['params'])
    elif command['action'] == 'trigger_i2c':
        trigger_i2c(**command['params']) 
    elif command['action'] == 'trigger_spi':
        trigger_spi(**command['params'])  
    elif command['action'] == 'trigger_pulse':
        trigger_pulse(**command['params'])              
    else:
        pass

if __name__ == '__main__':
    main()
