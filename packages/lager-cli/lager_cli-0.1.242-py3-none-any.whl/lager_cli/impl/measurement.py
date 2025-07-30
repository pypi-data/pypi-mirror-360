import os
import json
import time
from lager.pcb.net import Net, NetType, TriggerType,TriggerUARTParity,TriggerI2CDirection

def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass

def measure_vavg(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)   
    return target_net.measurement.voltage_average(display=display, measurement_cursor=cursor)

def measure_vmax(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)    
    return target_net.measurement.voltage_max(display=display, measurement_cursor=cursor)

def measure_vmin(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)    
    return target_net.measurement.voltage_min(display=display, measurement_cursor=cursor)

def measure_vpp(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)   
    return target_net.measurement.voltage_peak_to_peak(display=display, measurement_cursor=cursor)

def measure_vrms(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)   
    return target_net.measurement.voltage_rms(display=display, measurement_cursor=cursor)

def measure_period(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)   
    return target_net.measurement.period(display=display, measurement_cursor=cursor)

def measure_freq(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    return target_net.measurement.frequency(display=display, measurement_cursor=cursor)

def measure_dc_pos(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    return target_net.measurement.duty_cycle_positive(display=display, measurement_cursor=cursor) 

def measure_dc_neg(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    return target_net.measurement.duty_cycle_negative(display=display, measurement_cursor=cursor)        

def measure_pw_pos(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    return target_net.measurement.pulse_width_positive(display=display, measurement_cursor=cursor) 

def measure_pw_neg(netname, display, cursor):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    return target_net.measurement.pulse_width_negative(display=display, measurement_cursor=cursor) 

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] == 'measure_vavg':
        print(measure_vavg(**command['params']))
    elif command['action'] == 'measure_vmax':
        print(measure_vmax(**command['params']))
    elif command['action'] == 'measure_vmin':
        print(measure_vmin(**command['params']))
    elif command['action'] == 'measure_vpp':
        print(measure_vpp(**command['params']))
    elif command['action'] == 'measure_vrms':
        print(measure_vrms(**command['params']))
    elif command['action'] == 'measure_period':
        print(measure_period(**command['params']))
    elif command['action'] == 'measure_freq':
        print(measure_freq(**command['params']))
    elif command['action'] == 'measure_dc_pos':
        print(measure_dc_pos(**command['params']))
    elif command['action'] == 'measure_dc_neg':
        print(measure_dc_neg(**command['params']))
    elif command['action'] == 'measure_pulse_width_pos':
        print(measure_pw_pos(**command['params']))
    elif command['action'] == 'measure_pulse_width_neg':
        print(measure_pw_neg(**command['params']))                  
    else:
        pass

if __name__ == '__main__':
    main()