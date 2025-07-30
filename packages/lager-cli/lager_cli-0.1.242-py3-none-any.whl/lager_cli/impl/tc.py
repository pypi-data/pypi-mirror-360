from lager import lager
from lager.pcb.net import Net, NetType
import sys

def main():
    net = Net.get(sys.argv[1], type=NetType.Thermocouple)
    print(net.read())

if __name__ == '__main__':
    main()
