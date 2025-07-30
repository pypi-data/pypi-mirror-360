import os
import json
from lager.pcb.net import Net, NetType

def set_voltdiv(net, value):
    net.trace_settings.set_volts_per_div(float(value))

def set_timediv(net, value):
    net.trace_settings.set_time_per_div(float(value)) 

def set_voltoffset(net, value):
    net.trace_settings.set_volt_offset(float(value)) 

def set_timeoffset(net, value):
    net.trace_settings.set_time_offset(float(value))          


def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] != 'trace':
        raise RuntimeError(f'Incorrect command {command["action"]}')

    params = command['params']
    target_net = Net(params['netname'], type=None, setup_function=net_setup, teardown_function=net_teardown)
    if params['voltdiv']:
        set_voltdiv(target_net, params['voltdiv'])
    if params['timediv']:
        set_timediv(target_net, params['timediv'])
    if params['voltoffset']:
        set_voltoffset(target_net, params['voltoffset']) 
    if params['timeoffset']:
        set_timeoffset(target_net, params['timeoffset'])                        

if __name__ == '__main__':
    main()
