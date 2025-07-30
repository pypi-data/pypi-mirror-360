"""
    lager.devenv.commands

    Devenv commands
"""
import os
import itertools
import subprocess
from pathlib import Path
import click
from ..config import (
    read_config_file,
    write_config_file,
    add_devenv_command,
    remove_devenv_command,
    all_commands,
    find_devenv_config_path,
    make_config_path,
    get_devenv_config,
    DEVENV_SECTION_NAME,
    LAGER_CONFIG_FILE_NAME,
    get_global_config_file_path,
)


@click.group()
def devenv():
    """
        Lager devenv commands
    """
    pass

existing_dir_type = click.Path(
    exists=True,
    file_okay=False,
    dir_okay=True,
    readable=True,
    resolve_path=True,
)

@devenv.command()
@click.pass_context
@click.option('--image', prompt='Docker image', default='lagerdata/devenv-cortexm', show_default=True)
@click.option('--mount-dir', prompt='Source code mount directory in docker container',
              default='/app', show_default=True)
@click.option('--shell', help='Path to shell executable in docker image', default=None)
def create(ctx, image, mount_dir, shell):
    """
        Create a development environment
    """
    if shell is None:
        if image.startswith('lagerdata/'):
            shell = '/bin/bash'
        else:
            shell = click.prompt('Path to shell executable in docker image', default='/bin/bash')

    config_path = find_devenv_config_path()
    if config_path is not None:
        answer = click.confirm('Config file {} exists; overwrite?'.format(config_path))
        if not answer:
            ctx.exit(0)

    if config_path is None:
        config_path = make_config_path(os.getcwd())
        Path(config_path).touch()

    config = read_config_file(config_path)
    if not config.has_section(DEVENV_SECTION_NAME):
        config.add_section(DEVENV_SECTION_NAME)
    config.set(DEVENV_SECTION_NAME, 'image', image)
    config.set(DEVENV_SECTION_NAME, 'mount_dir', mount_dir)
    config.set(DEVENV_SECTION_NAME, 'shell', shell)
    write_config_file(config, config_path)

@devenv.command()
@click.pass_context
@click.option('--mount', '-m', help='Name of volume to mount', required=False)
@click.option('--user', '-u', help='User to run as', required=False, default=None)
@click.option('--group', '-g', help='Group to run as', required=False, default=None)
@click.option('--name', '-n', help='Set Container name', required=False)
@click.option('--detach/--no-detach', '-d', help='Run container as detached', required=False, default=False,is_flag=True)
@click.option('--port', '-p', help='Do port forwarding', required=False, multiple=True)
@click.option('--entrypoint', help='entrypoint', required=False)
@click.option('--network', help='Network mode', required=False)
@click.option('--platform', help='Platform', required=False)
def terminal(ctx, mount, user, group, name, detach, port, entrypoint, network, platform):
    """
        Start an interactive terminal for a docker image
    """
    path, config = get_devenv_config()
    section = config[DEVENV_SECTION_NAME]

    image = section.get('image')
    source_dir = os.path.dirname(path)
    mount_dir = section.get('mount_dir')
    working_dir = mount_dir
    args = [
        'docker',
        'run',
        '-it',
        '--init',
    ]
    ssh_sock = os.getenv('SSH_AUTH_SOCK')
    if ssh_sock:
        args.extend(['-v', f'{ssh_sock}:{ssh_sock}', '-e', f'SSH_AUTH_SOCK={ssh_sock}'])

    keypath = Path(os.getenv('HOME', ''), '.ssh/id_ed25519')
    if keypath.is_file():
        args.extend(['-v', f'{keypath}:/root/.ssh/id_ed25519:ro'])

    known_hosts = Path(os.getenv('HOME', ''), '.ssh/known_hosts')
    if known_hosts.is_file():
        args.extend(['-v', f'{known_hosts}:/root/.ssh/known_hosts:ro'])

    repo_root_relative_path = section.get('repo_root_relative_path')

    if 'user' in section:
        user = section['user']
    if 'group' in section:
        group = section['group']
    macaddr = None
    if 'macaddr' in section:
        macaddr = section['macaddr']

    hostname = None
    if 'hostname' in section:
        hostname = section['hostname']

    if entrypoint:
        args.extend(['--entrypoint', entrypoint])

    if user:
        args.extend(['--user', user])
    if group:
        args.extend(['--group', group])
    if macaddr:
        args.extend(['--mac-address', macaddr])
    if hostname:
        args.extend(['--hostname', hostname])

    if mount:
        args.extend(['--mount', f'source={mount},target={mount_dir}'])
    else:
        if repo_root_relative_path:
            root = Path(os.path.join(source_dir, repo_root_relative_path)).resolve()
            if source_dir.startswith(str(root)):
                trailing = source_dir[len(str(root)):]
                if trailing.startswith('/'):
                    trailing = trailing[1:]
                working_dir = os.path.join(mount_dir, trailing)
            source_dir = root

        args.extend(['-v', f'{source_dir}:{mount_dir}'])

    if name:
        args.extend(['--name', name])

    if network:
        args.append(f'--network={network}')

    args.extend(itertools.chain(*zip(itertools.repeat('-p'), port)))

    if platform:
        args.extend(['--platform', platform])

    if detach:
        args.extend(['-d'])
    else:
        args.extend(['--rm'])

    global_config_path = get_global_config_file_path()
    if os.path.exists(global_config_path):
        args.extend([
            '--env=LAGER_CONFIG_FILE_DIR=/lager',
            '-v',
            f'{global_config_path}:/lager/{LAGER_CONFIG_FILE_NAME}'
        ])

    args.extend(['-w', working_dir])

    args.append(image)

    proc = subprocess.run(args, check=False)
    ctx.exit(proc.returncode)


@devenv.command()
@click.confirmation_option(prompt='Are you sure you want to delete your devenv?')
def delete():
    """
        Delete devenv config
    """
    config_path = find_devenv_config_path()
    if not config_path or not os.path.exists(config_path):
        return

    os.remove(config_path)

@devenv.command()
@click.argument('command_name')
@click.argument('command', required=False)
@click.option('--warn/--no-warn', default=True, help='Whether to print a warning if overwriting an existing command.', show_default=True)
def add_command(command_name, command, warn):
    """
        Add COMMAND to devenv with the name COMMAND_NAME
    """
    path, config = get_devenv_config()
    section = config[DEVENV_SECTION_NAME]
    if not command:
        command = click.prompt('Please enter the command')

    add_devenv_command(section, command_name, command, warn)
    write_config_file(config, path)

@devenv.command()
@click.argument('command_name')
@click.option('--devenv', '_devenv', help='Delete command from devenv named `foo`', metavar='foo')
def delete_command(command_name, _devenv):
    """
        Delete COMMAND_NAME from devenv
    """
    path, config = get_devenv_config()
    section = config[DEVENV_SECTION_NAME]

    remove_devenv_command(section, command_name)
    write_config_file(config, path)


@devenv.command()
def commands():
    """
        List the commands in a devenv
    """
    _, config = get_devenv_config()
    section = config[DEVENV_SECTION_NAME]
    for name, command in all_commands(section).items():
        click.secho(name, fg='green', nl=False)
        click.echo(f': {command}')
