from lager import lager
from lager.pcb.net import Net, NetType
import sys

def main():
    net = Net.get(sys.argv[1], type=NetType.DAC)
    if len(sys.argv) == 2:
        print(net.input())
    elif len(sys.argv) == 3:
        value = float(sys.argv[2])
        net.output(value)
    else:
        raise RuntimeError('Invalid DAC command')

if __name__ == '__main__':
    main()
