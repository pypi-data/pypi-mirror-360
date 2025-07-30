import sys
import time
from lager.pydexarm import Dexarm, get_arm_device

def parse_float(val):
    if val == 'None':
        return None
    return float(val)

def print_position(position):
    (x, y, z, extrusion, theta_a, theta_b, theta_c) = position
    print(f'X: {x} Y: {y} Z: {z}')

def get_position(device):
    with Dexarm(port=device) as arm:
        position = arm.get_current_position()
        print_position(position)

def disable_motor(device):
    with Dexarm(port=device) as arm:
        arm.disable_motor()

def enable_motor(device):
    with Dexarm(port=device) as arm:
        arm.enable_motor()

def read_and_save_position(device):
    with Dexarm(port=device) as arm:
        arm.read_and_save_position()

def delta(device):
    with Dexarm(port=device) as arm:
        (x, y, z, extrusion, theta_a, theta_b, theta_c) = arm.get_current_position()

        delta_x = parse_float(sys.argv[2]) or 0.0
        delta_y = parse_float(sys.argv[3]) or 0.0
        delta_z = parse_float(sys.argv[4]) or 0.0

        new_x = delta_x + x
        new_y = delta_y + y
        new_z = delta_z + z

        arm.move_to_blocking(new_x, new_y, new_z, timeout=5.0)
        time.sleep(0.1)
        position = arm.get_current_position()
        print_position(position)


def move(device):
    with Dexarm(port=device) as arm:
        (x, y, z, extrusion, theta_a, theta_b, theta_c) = arm.get_current_position()

        x = parse_float(sys.argv[2]) or x
        y = parse_float(sys.argv[3]) or y
        z = parse_float(sys.argv[4]) or z
        arm.move_to_blocking(x, y, z, timeout=5.0)

        time.sleep(0.1)
        position = arm.get_current_position()
        print_position(position)

def go_home(device):
    with Dexarm(port=device) as arm:
        arm.go_home()    

def main():

    command = sys.argv[1]
    serial = sys.argv[-1]
    if serial == 'None':
        serial = None
    device = get_arm_device(serial)

    if command == 'position':
        get_position(device)
    elif command == 'disable_motor':
        disable_motor(device)
    elif command == 'enable_motor':
        enable_motor(device)
    elif command == 'read_and_save_position':
        read_and_save_position(device)
    elif command == 'delta':
        delta(device)
    elif command == 'move':
        move(device)
    elif command == 'go_home':
        go_home(device)


if __name__ == '__main__':
    main()
