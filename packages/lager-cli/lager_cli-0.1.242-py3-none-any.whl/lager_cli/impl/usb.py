import sys
import json
from lager.usb import USBDevice

def main():
    data = json.loads(sys.argv[1])
    action = data['action']
    device_name = data['device']
    if action is None:
        for device in USBDevice.all():
            if device_name is None or device_name == device.name:
                print(f'{device.name} - powered: {device.is_enabled()}')
    else:
        try:
            device = USBDevice.find(device_name)
        except RuntimeError as exc:
            raise SystemExit(f'Device {device_name} not found') from exc

        if action == 'on':
            device.on()
        elif action == 'off':
            device.off()
        elif action == 'toggle':
            device.toggle()

if __name__ == '__main__':
    main()
