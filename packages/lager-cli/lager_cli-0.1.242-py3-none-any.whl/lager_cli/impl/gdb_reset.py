import sys
import time
from lager import gdb

def main():
    halt = sys.argv[1] == 'True'
    try:
        resp = gdb.reset(halt)
    except gdb.DebuggerNotConnectedError as exc:
        item = exc.args[0]
        if item and item.get('payload') and item['payload'].get('msg') == 'Remote connection closed':
            print('Debugger not connected')
            raise SystemExit(1)
        raise

    for item in resp:
        if item['message'] is None and item['payload'] is not None and item['stream'] == 'stdout':
            print(item['payload'], end='')


if __name__ == '__main__':
    main()
