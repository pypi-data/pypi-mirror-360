import click

from dataset_sh.clients.locator import DatasetLocator
from dataset_sh.clients.obj import Remote, RemoteDataset, LocalStorage, remote
from dataset_sh.utils.misc import parse_tags


class RemoteCtx(object):
    remote: Remote

    def __init__(self, host, profile):
        self.remote = remote(host, profile)


@click.group(name='remote')
@click.option('--host', '-h', 'host', help='host address or alias.', default=None)
@click.option('--profile', '-p', 'profile_name', help='profile name.', default=None)
@click.pass_context
def remote_cli(ctx, host, profile_name):
    """to interact with dataset.sh remote server"""
    ctx.obj = RemoteCtx(host, profile_name)


@remote_cli.command(name='set-tag')
@click.argument('name')
@click.argument('tag')
@click.argument('version')
@click.pass_obj
def tag_remote(remote_ctx: RemoteCtx, name, version, tag):
    """set a version tag for a dataset on a remote server."""
    remote_ctx.remote.dataset(name).set_tag(tag, version)


@remote_cli.command(name='tag-info')
@click.argument('name')
@click.argument('tag')
@click.pass_obj
def print_tag_remote(remote_ctx: RemoteCtx, name, tag):
    """resolve a dataset version tag to version"""
    result = remote_ctx.remote.dataset(name).resolve_tag(tag)
    click.echo(result.version)


@remote_cli.command(name='list-versions')
@click.argument('name')
@click.pass_obj
def list_remote_versions(remote_ctx: RemoteCtx, name):
    """List all available versions of a dataset on a remote server"""

    versions = remote_ctx.remote.dataset(name).versions()
    for v in versions.items:
        click.echo(v.version)


@remote_cli.command(name='download')
@click.argument('name')
@click.option('--file', '-f', default=None,
              help='if this option is provided, the dataset will be downloaded to a file.')
@click.option('--dest', '-d', default=None,
              help='download to local and rename to this name. if file option is provided, this will be ignored.')
@click.option('--tag', '-t', help='tag this version in local.', default='')
@click.pass_obj
def download_remote(remote_ctx: RemoteCtx, name, dest, file, tag):
    """
        download dataset [NAME] from remote.
    """
    remote_dataset_version = DatasetLocator.from_str(name).resolve_remote(remote_ctx.remote)
    if file:
        remote_dataset_version.download_to_file(file)
    else:
        if dest is None:
            dest = name
        local_dataset = DatasetLocator.from_str(dest).resolve_local_dataset()
        remote_dataset_version.download_to(local_dataset, parse_tags(tag))


@remote_cli.command(name='upload')
@click.argument('target_name')
@click.option('--source', '-s', help='use this option to select version to upload', default=None)
@click.option('--tag', '-t', help='tag name of this version in remote.', default='')
@click.pass_obj
def upload(remote_ctx: RemoteCtx, target_name, source, tag):
    """upload managed dataset to server"""
    remote_dataset = DatasetLocator.from_str(target_name).resolve_remote_dataset(remote_ctx.remote)
    if source is None:
        source = target_name
    local_source = DatasetLocator.from_str(source).resolve_local()
    remote_dataset.upload_from_local(local_source, parse_tags(tag))
    local_dataset_source = DatasetLocator.from_str(source).resolve_local_dataset()
    readme = local_dataset_source.readme()
    if readme:
        remote_dataset.update_readme(readme)
    # remote_dataset.upload_from_local(local_source, parse_tags(tag))


@remote_cli.command(name='upload-file')
@click.argument('file')
@click.argument('target_name')
@click.option('--tag', '-t', help='tag name of this version in remote.', default='')
@click.pass_obj
def upload_file(remote_ctx: RemoteCtx, file, target_name, tag):
    """upload dataset to server from a dataset file"""
    remote_dataset = DatasetLocator.from_str(target_name).resolve_remote_dataset(remote_ctx.remote)
    remote_dataset.upload_from_file(file, parse_tags(tag))


@remote_cli.command(name='test-connection')
@click.pass_obj
def test_connection(remote_ctx: RemoteCtx):
    """test connection to remote"""
    user_info = remote_ctx.remote.test_connection()
    username = user_info['username']
    if username:
        click.echo(f"Logged in as {username}")
    else:
        click.echo(f"You are a visitor to this server")
