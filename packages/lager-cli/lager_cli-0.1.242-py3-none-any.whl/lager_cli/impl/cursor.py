import os
import json
import time
from lager.pcb.net import Net, NetType, TriggerType,TriggerUARTParity,TriggerI2CDirection

def net_setup(*args, **kwargs):
    pass

def net_teardown(*args, **kwargs):
    pass

def set_cursor_a(netname, x, y):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.cursor.set_a(x=x, y=y)

def move_cursor_a(netname, del_x, del_y):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.cursor.move_a(x_del=del_x, y_del=del_y)

def set_cursor_b(netname, x, y):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.cursor.set_b(x=x, y=y)

def move_cursor_b(netname, del_x, del_y):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.cursor.move_b(x_del=del_x, y_del=del_y)

def hide_cursor(netname):
    target_net = Net(netname, type=None, setup_function=net_setup, teardown_function=net_teardown)
    target_net.cursor.hide() 

def main():
    command = json.loads(os.environ['LAGER_COMMAND_DATA'])
    if command['action'] == 'set_a':
        set_cursor_a(**command['params'])
    elif command['action'] == 'move_a':
        move_cursor_a(**command['params'])
    elif command['action'] == 'set_b':
        set_cursor_b(**command['params'])
    elif command['action'] == 'move_b':
        move_cursor_b(**command['params']) 
    elif command['action'] == 'hide_cursor':
        hide_cursor(**command['params'])                         
    else:
        pass

if __name__ == '__main__':
    main()