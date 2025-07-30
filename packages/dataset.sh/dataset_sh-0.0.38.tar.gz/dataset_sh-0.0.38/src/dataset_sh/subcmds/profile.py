import click

from dataset_sh.remote_utils.profile import DatasetClientProfileConfig, ask_hostname, ask_name, ask_access_key, \
    ask_override
import dataset_sh.constants as DatasetConstants


@click.group(name='profile')
def profile_cli():
    """to manage dataset.sh remote profiles"""
    pass


@profile_cli.command(name='add')
@click.option('--name', '-n', 'name', help='profile name.', default=None)
@click.option('--host', '-h', 'host', help='host address or alias.', default=None)
@click.option('--force', '-f', 'force',
              is_flag=True, help='force override existing profile.',
              default=False)
def add_profile(name, host, force):
    """
    Add access key to dataset.sh client.
    """
    cfg = DatasetClientProfileConfig.load_profiles()
    if host is None or host.strip() == '':
        host = ask_hostname('https://base.dataset.sh')

    if name is None:
        name = ask_name()

    if cfg.get_profile(name):
        click.echo("")
        click.echo('Find existing profile with the same name.')
        if not force:
            if not ask_override():
                raise ValueError(f'Profile {name} exists.')

    key = ask_access_key()

    cfg.set_profile(host, key, name=name)
    cfg.save()

    click.echo(f'Profile saved in {DatasetConstants.CONFIG_JSON}')


@profile_cli.command(name='list')
def list_profile():
    """
    List remote profiles.
    """
    cfg = DatasetClientProfileConfig.load_profiles()
    for p in cfg.profiles:
        if p.name:
            click.echo(f"Profile: {p.name}")
        click.echo(f"Host: {p.host}")
        click.echo('\n')


@profile_cli.command(name='print')
@click.argument('name')
def print_profile(name):
    """
    print remote profile information.
    """
    profile = DatasetClientProfileConfig.load_profiles().get_profile(name)
    if profile:
        click.echo(f'Profile: {profile.name}')
        click.echo(f'Host: {profile.host}')
    else:
        raise ValueError(f'profile {name} does not exist')


@profile_cli.command(name='remove')
@click.argument('name')
def remove_profile(name):
    """
    Remove existing profile.
    """
    DatasetClientProfileConfig.load_profiles().remove_profile(name).save()
