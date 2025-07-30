import json
import click
import asyncio
import os
import sys
import io
from textual.app import App, ComposeResult
from textual.widgets import Footer, Input, Static
from textual.containers import Vertical
from textual.reactive import reactive
from textual.events import Key
from ..context import get_default_gateway, get_impl_path
from ..python.commands import run_python_internal
from ..net.supply_commands import validate_net
import logging
from rich import print
from contextlib import redirect_stdout

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='[%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("supply_tui.log"),
#         logging.StreamHandler()
#     ]
# )
# log = logging.getLogger("supply_tui")

@click.command()
@click.argument('netname', required=True)
@click.option('--gateway', required=False)
@click.option('--dut', required=False)
@click.pass_context
def supply_tui(ctx, netname, gateway, dut):
    gateway = gateway or dut
    if gateway is None:
        gateway = get_default_gateway(ctx)

    if not validate_net(ctx, gateway, netname, 'power-supply'):
        print(f"{netname} is not a supply net")
        return

    try:
        # log.debug("Starting SupplyTUI...")
        app = SupplyTUI(ctx, netname, gateway, dut)
        asyncio.run(app.run_async())
    except Exception:
        # log.exception("TUI crashed:")
        raise

class CommandOutput(Static):
    text = reactive("Welcome to Supply TUI\nType 'voltage 3.3' to set voltage, 'voltage' to read, or 'q' to quit.")

    def render(self) -> str:
        return self.text

class CommandInput(Input):
    pass

class SupplyTUI(App):
    command_history = []
    history_index = -1
    CSS_PATH = None

    def __init__(self, ctx, netname, gateway, dut):
        super().__init__()
        self.ctx = ctx
        self.netname = netname
        self.gateway = gateway
        self.dut = dut

    CSS = """
    Screen {
        background: black;
        color: white;
    }
    Input {
        border: round green;
        background: #111;
        color: white;
    }
    Static {
        padding: 1;
        border: round yellow;
        background: #222;
        color: white;
    }
    Footer {
        background: #444;
        color: white;
    }
    """

    def compose(self) -> ComposeResult:
        self.output = CommandOutput()
        self.command_input = CommandInput(placeholder="Enter command (e.g. voltage 3.3 or voltage) — type 'q' to quit")
        yield Vertical(self.output, self.command_input)
        yield Footer()

    async def on_mount(self) -> None:
        self.command_input.focus()

    async def on_key(self, event: Key):
        if event.key == "up" and self.command_history:
            self.history_index = max(0, self.history_index - 1)
            self.command_input.value = self.command_history[self.history_index]
        elif event.key == "down" and self.command_history:
            self.history_index = min(len(self.command_history) - 1, self.history_index + 1)
            self.command_input.value = self.command_history[self.history_index]

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value.strip().split()
        if not command:
            return

        try:
            if command[0] == "voltage":
                if len(command) == 2:
                    self.run_backend("voltage", value=float(command[1]))
                    self.output.text = f"[SET] Voltage set to {command[1]} V"
                else:
                    # voltage = self.read_voltage()
                    voltage = self.run_backend("get_voltage", value=None)
                    if voltage is not None:
                        self.output.text = f"[READ] Voltage: {voltage} V"
                    else:
                        self.output.text = "[READ] Voltage not found in output."
            elif command[0] == "current":
                if len(command) == 2:
                    self.run_backend("current", value=float(command[1]))
                    self.output.text = f"[SET] Voltage set to {command[1]} V"
                else:
                    # voltage = self.read_voltage()
                    voltage = self.run_backend("get_current", value=None)
                    if voltage is not None:
                        self.output.text = f"[READ] Current: {voltage} V"
                    else:
                        self.output.text = "[READ] Current not found in output."
            elif command[0] == "q":
                self.exit()
            else:
                self.output.text = f"Unknown command: {' '.join(command)}"
        except Exception as e:
            self.output.text = f"Error: {e}"
            # log.exception("Exception in on_input_submitted:")

        self.command_history.append(event.value.strip())
        self.history_index = len(self.command_history)
        self.command_input.value = ""



    def run_backend(self, action, value=None, mcu=None):
        data = {
            'action': action,
            'mcu': mcu,
            'params': {'netname': self.netname}
        }
        if value is not None:
            data['params']['value'] = value

        env = (f"LAGER_COMMAND_DATA={json.dumps(data)}",)
        buf = io.StringIO()

        # log.debug(f"[TUI] Sending {action} action with data: {data}")

        try:
            with redirect_stdout(buf):
                run_python_internal(
                    self.ctx,
                    get_impl_path('supply.py'),
                    self.dut,
                    image='',
                    env=env,
                    passenv=(),
                    kill=False,
                    download=(),
                    allow_overwrite=False,
                    signum='SIGTERM',
                    timeout=0,
                    detach=False,
                    port=(),
                    org=None,
                    args=(),
                )
        except SystemExit:
            pass  # Prevent app from exiting

        output = buf.getvalue()
        # log.debug(f"[TUI] Captured backend output:\n{output}")
        # Set output text based on the action
        if action == "voltage" and value is not None:
            self.output.text = f"[SET] Voltage set to {value} V"
        elif action == "get_voltage" and output is not None:
            for line in output.splitlines():
                if line.startswith("Voltage:"):
                    return line.split(":")[1].strip()
        elif action == "get_current" and output is not None:
            for line in output.splitlines():
                if line.startswith("Current:"):
                    return line.split(":")[1].strip()
        elif output.strip():
            self.output.text = output.strip()
        else:
            self.output.text = f"[{action.upper()}] No output returned."

