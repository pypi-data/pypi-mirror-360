import usb.core
import usb.util

def main():
    # find all devices
    devices = usb.core.find(find_all=True)

    # iterate through devices and print info
    for device in devices:
        print(f"Device: idVendor=0x{device.idVendor:04x}, idProduct=0x{device.idProduct:04x}")
        try:
            manufacturer = usb.util.get_string(device, device.iManufacturer)
            product = usb.util.get_string(device, device.iProduct)
            serial = usb.util.get_string(device, device.iSerialNumber)
            print(f"  Manufacturer: {manufacturer}")
            print(f"  Product:      {product}")
            print(f"  Serial No:    {serial}")
        except usb.core.USBError as e:
            print(f"  Could not retrieve strings: {e}") 
if __name__ == '__main__':
    main()
