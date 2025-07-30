import os
import json
import time
from lager.pcb.net import Net, NetType

def control_voltage(netname, value, voltage_max, current_max):
    pass

def control_current(netname, value, voltage_max, current_max):
    pass

def control_resistance(netname, value, voltage_max, current_max):
    pass

def control_power(netname, value, voltage_max, current_max):
    pass

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] == 'voltage':
        control_voltage(**command['params'])
    elif command['action'] == 'current':
        control_current(**command['params'])  
    elif command['action'] == 'resistance':
        control_resistance(**command['params'])    
    elif command['action'] == 'power':
        control_power(**command['params'])                                     
    else:
        pass

if __name__ == '__main__':
    main()