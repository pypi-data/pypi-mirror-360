from lager import lager
from lager.pcb.net import Net, NetType
import sys

def main():
    net = Net.get(sys.argv[1], type=NetType.ADC)
    print(net.input())

if __name__ == '__main__':
    main()
