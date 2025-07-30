"""
    lager.lister.commands

    List commands
"""
import click
from texttable import Texttable
from .. import SUPPORTED_DEVICES
from ..config import read_config_file

@click.group(name='list')
def lister():
    """
        Lager list commands
    """
    pass

def gateway_number(organizations, gateway):
    for org in organizations:
        if org['abbreviation'] and gateway['organization_id'] == org['id'] and gateway['id_within_organization']:
            return f'{org["abbreviation"]}-{gateway["id_within_organization"]}'

    return gateway['id']

def gateways(ctx):
    """
        List a user's gateways
    """

    session = ctx.obj.session
    resp = session.list_gateways()
    resp.raise_for_status()

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 'i'])
    table.set_cols_align(["l", "r"])
    table.add_row(['name', 'id'])

    data = resp.json()
    for gateway in data['gateways']:
        table.add_row([gateway['name'], gateway_number(data['organizations'], gateway)])
    click.echo(table.draw())


@lister.command('gateways', hidden=True)
@click.pass_context
def gateways_handler(ctx):
    """
        List a user's gateways
    """
    gateways(ctx)

@lister.command('duts')
@click.pass_context
def duts_handler(ctx):
    """
        List a user's DUTs
    """
    gateways(ctx)

@lister.command()
def supported_devices():
    """
        List supported devices
    """
    for device in SUPPORTED_DEVICES:
        click.echo(device)

@lister.command()
def secret_token():
    """
        Show the secret token, which can be used within a third-party CI system to auth lager-cli
    """
    config = read_config_file()
    click.echo(config['AUTH']['refresh'])
