import sys
import time
from lager import Net, NetType

def main():
    netname = sys.argv[1]
    net = Net.get(netname, type=NetType.Actuate)
    net.actuate()


if __name__ == '__main__':
    main()
