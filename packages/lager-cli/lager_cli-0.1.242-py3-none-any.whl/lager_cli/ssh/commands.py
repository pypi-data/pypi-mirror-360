"""
    lager.ssh.commands

    SSH commands
"""
import click
from ..context import get_default_gateway
import os
import time
import tempfile

@click.command()
@click.pass_context
@click.option('--dut', required=False, help='ID of DUT')
@click.option('--save-keys', is_flag=True, default=False)
@click.option('--phone-tunnel', is_flag=True, default=False, hidden=True)
def ssh(ctx, dut, save_keys, phone_tunnel):
    """
    SSH to the specified gateway
    """
    if dut is None:
        dut = get_default_gateway(ctx)

    session = ctx.obj.session
    resp = session.get_ssh_info(dut)
    data = resp.json()
    key_filename = None
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        key_filename = f.name
        f.write(data['privkey'].encode())

    pid = os.fork()
    command = [
        "ssh",
        "-i",
        str(key_filename),
        "-p",
        str(data['port']),
        f"{data['username']}@{data['host']}",
    ]
    extra = data.get('extra', {})
    extra_args = extra.get('args', [])
    if phone_tunnel:
        command.extend(extra_args)

    if pid > 0:
        """Parent process"""
        if save_keys:
            click.echo(' '.join(command))
        else:
            full = [command[0]] + command
            os.execlp(*full)

    else:
        """Child process"""
        if not save_keys:
            time.sleep(2)
            os.remove(key_filename)
