import os
import json
from ast import literal_eval
import time
from lager.pcb.net import Net, SimMode, NetType
from lager.pcb.defines import Mode
from lager.pcb.device import DeviceError


def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass

def set_mode(netname, mode_type):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if mode_type is None:
        mode_type = f"{target_net.mode()}"
        d = literal_eval(mode_type)
        if d['__enum__']['value']=='DYN':
            print("Dynamic")
        elif d['__enum__']['value']=='STAT':
            print("Static")
        else:
            raise Exception(f"Unknown type {mode_type}")
    else:
        if mode_type.lower() == 'static':
            target_net.setup_battery(sim_mode=SimMode.Static)
        elif mode_type.lower() == 'dynamic':
            target_net.setup_battery(sim_mode=SimMode.Dynamic)
        else:
            raise ValueError(f"{mode_type} is not a valid option")

def set_soc(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"SOC: {target_net.soc()}")
    else:
        if 0 > value < 100:
            raise SystemExit("SOC must be between 0 and 100")

        target_net.set_mode(Mode.BatterySimulator)
        target_net.set_sim_state_of_charge(value)

def set_voc(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"VOC: {target_net.voc()}")
    else:
        target_net.setup_battery(voc=value)

def set_volt_full(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"Battery Fully Charged Voltage: {target_net.voltage_full()}")
    else:
        target_net.setup_battery(voltage_full=value)

def set_volt_empty(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"Battery Fully Discharged Voltage: {target_net.voltage_empty()}")
    else:
        target_net.setup_battery(voltage_empty=value)

def set_capacity(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"Battery Max Capacity: {target_net.capacity()}")
    else:
        target_net.setup_battery(capacity=value)

def set_current_limit(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"Max Charge/Discharge Current: {target_net.current_limit()}")
    else:
        target_net.setup_battery(current_limit=value)

def set_ovp(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"Over Voltage Protection Value: {target_net.ovp_level()}")
    else:
        target_net.set_over_voltage(value)

def set_ocp(netname, value):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    if value is None:
        print(f"Over Current Protection Value: {target_net.ocp_level()}")
    else:
        target_net.set_over_current(value)

def set_model(netname, partnumber):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    target_net.setup_battery(        
            model=partnumber)

def enable_battery(netname):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    try:
        target_net.enable()
    except DeviceError as exc:
        try:
            response = json.loads(exc.args[0])
            print(response['message'])
        except:
            raise exc
        raise SystemExit(1)

def disable_battery(netname):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    target_net.disable()

def state(netname):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    tvolt = target_net.terminal_voltage()
    voc = target_net.voc()
    current = target_net.current()
    esr = target_net.esr()
    soc = target_net.soc()
    capacity = target_net.capacity()

    print(f"Terminal Voltage:{tvolt}")
    print(f"Current:{current}")
    print(f"ESR:{esr}")
    print(f"SOC:{soc}")
    print(f"VOC:{voc}")
    print(f"Capacity:{capacity}") 

def set_to_battery_mode(netname):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    target_net.set_mode(Mode.BatterySimulator)

def clear(netname):
    target_net = Net(netname, type=NetType.Battery, setup_function=net_setup, teardown_function=net_teardown)
    try:
        target_net.clear_battery_output_protection()
    except DeviceError as exc:
        try:
            response = json.loads(exc.args[0])
            if 'OVP (over voltage) error occurred' in response['message'] or 'OCP (over current) error occurred' in response['message']:
                return
            raise exc
        except:
            raise exc
def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] == 'set_mode':
        set_mode(**command['params'])
    elif command['action'] == 'set_soc':
        set_soc(**command['params'])  
    elif command['action'] == 'set_voc':
        set_voc(**command['params'])
    elif command['action'] == 'set_volt_full':
        set_volt_full(**command['params']) 
    elif command['action'] == 'set_volt_empty':
        set_volt_empty(**command['params'])   
    elif command['action'] == 'set_capacity':
        set_capacity(**command['params'])
    elif command['action'] == 'set_current_limit':
        set_current_limit(**command['params'])   
    elif command['action'] == 'set_ovp':
        set_ovp(**command['params'])    
    elif command['action'] == 'set_ocp':
        set_ocp(**command['params']) 
    elif command['action'] == 'state':
        state(**command['params'])   
    elif command['action'] == 'enable_battery':
        enable_battery(**command['params'])  
    elif command['action'] == 'disable_battery':
        disable_battery(**command['params'])
    elif command['action'] == 'set_model':
        set_model(**command['params'])                                                                                                
    elif command['action'] == 'set_to_battery_mode':
        set_to_battery_mode(**command['params'])
    elif command['action'] == 'clear':
        clear(**command['params'])
    else:
        pass

if __name__ == '__main__':
    main()