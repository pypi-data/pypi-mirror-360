import sys
import json
from lager.pcb.net import Net, NetType
from lager.usb import USBDevice

def main():
    data = json.loads(sys.argv[1])
    net = Net.get(data['netname'], type=NetType.GPIO)

    if data['action'] == 'input':
        print(int(net.input()))
    elif data['action'] == 'output':
        if data['level'].lower() in ('on', 'high'):
            net.output(1)
        elif data['level'].lower() in ('off', 'low'):
            net.output(0)
        else:
            raise ValueError(f'Invalid level {data["level"]}')
    else:
        raise ValueError(f'invalid action {data["action"]}')

if __name__ == '__main__':
    main()
