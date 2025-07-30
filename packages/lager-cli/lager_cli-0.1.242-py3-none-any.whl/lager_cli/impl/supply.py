import os
import json
import time
from lager.pcb.net import Net, NetType
from lager.pcb.defines import Mode
from lager.pcb.device import DeviceError

def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass

def set_voltage(target_net, value=None, ocp=None, ovp=None, **kwargs):
    if ocp != None:
        target_net.set_ocp(ocp)
    if ovp != None:
        target_net.set_ovp(ovp)

    if value != None:
        target_net.set_voltage(value)
        return

    print(f"Voltage: {target_net.voltage()}")

def set_current(target_net, value=None, ocp=None, ovp=None, **kwargs):
    if ocp != None:
        target_net.set_ocp(ocp)
    if ovp != None:
        target_net.set_ovp(ovp)

    if value != None:
        target_net.set_current(value)
        return

    print(f"Current: {target_net.current()}")


def set_ovp(target_net, ovp, **kwargs):
    target_net.set_ovp(ovp)


def set_ocp(target_net, ocp, **kwargs):
    target_net.set_ocp(ocp)

def clear_ovp(target_net, **kwargs):
    try:
        target_net.clear_ovp()
    except DeviceError as exc:
        if b'OVP' in exc.args[0] or b'over voltage' in exc.args[0] or b'overvoltage' in exc.args[0]:
            target_net.clear_ovp()

def clear_ocp(target_net, **kwargs):
    try:
        target_net.clear_ocp()
    except DeviceError as exc:
        if b'OCP' in exc.args[0] or b'overcurrent' in exc.args[0]:
            target_net.clear_ocp()

def get_state(target_net, **kwargs):
    print(f"Voltage: {target_net.voltage()}")
    print(f"Current: {target_net.current()}")
    print(f"Power: {target_net.power()}")
    print(f"Over Current Limit {target_net.get_ocp_limit()}")
    print(f"    Net in Over Current: {target_net.is_ocp()}")
    print(f"Over Voltage Limit {target_net.get_ovp_limit()}")
    print(f"    Net in Over Voltage: {target_net.is_ovp()}")


def get_power(target_net, **kwargs):
    print(f"Power: {target_net.power()}")

def get_ocp(target_net, **kwargs):
    print(f"OCP: {target_net.get_ocp_limit()}")


def get_ovp(target_net, **kwargs):
    print(f"OVP: {target_net.get_ovp_limit()}")

def is_ocp(target_net, **kwargs):
    print(f"OCP Status: {target_net.is_ocp()}")

def is_ovp(target_net, **kwargs):
    print(f"OVP Status: {target_net.is_ovp()}")


def disable_net(target_net, **kwargs):
    target_net.disable()

def enable_net(target_net, **kwargs):
    target_net.enable()

def set_supply_mode(target_net, **kwargs):
    target_net.set_mode(Mode.PowerSupply)



DISPATCH = {
    'voltage': set_voltage,
    'current': set_current,
    'get_state': get_state,
    'disable_net': disable_net,
    'enable_net': enable_net,
    'set_mode': set_supply_mode,
    'clear_ovp': clear_ovp,
    'clear_ocp': clear_ocp,
    'get_voltage': set_voltage,
    'get_current': set_current,
    'set_ocp': set_ocp,
    'set_ovp': set_ovp,
    'get_ocp': get_ocp,
    'get_ovp': get_ovp,
    'is_ocp': is_ocp,
    'is_ovp': is_ovp,
}

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    netname = command['params'].pop('netname')
    target_net = Net(netname, type=NetType.PowerSupply, setup_function=net_setup, teardown_function=net_teardown)

    action = command['action']
    handler = DISPATCH.get(action)
    if handler:
        handler(target_net, **command['params'])

if __name__ == '__main__':
    main()
