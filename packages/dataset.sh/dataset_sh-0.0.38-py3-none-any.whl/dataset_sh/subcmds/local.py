import json
from typing import Optional

import click
from click import BadParameter

from dataset_sh.clients.obj import LocalStorage
from dataset_sh.constants import DEFAULT_COLLECTION_NAME
from dataset_sh.utils.misc import parse_tags
from dataset_sh.utils.usage.read_data_codegen import get_read_data_code


def _get_dataset_version(ctx, name, version, tag):
    dataset = ctx.local_storage.dataset(name)
    if version:
        dv = dataset.version(version)
    elif tag:
        dv = dataset.tag(tag)
    else:
        dv = dataset.latest()
    return dv


class LocalCtx(object):

    def __init__(self, folder: Optional[str]):
        self.folder = folder
        self.local_storage = LocalStorage(folder)


@click.group(name='local')
@click.option('--folder', '-f', 'folder', help='location of the dataset storage folder', default=None)
@click.pass_context
def local_cli(ctx, folder):
    """to interact with dataset.sh local storage"""
    ctx.obj = LocalCtx(folder)


@local_cli.command(name='import-as-latest')
@click.argument('name')
@click.argument('file')
@click.option('--tag', '-t', default='', help='additional tags')
@click.pass_obj
def import_as_latest(ctx, name, file, tag):
    """import dataset from file, and automatically tag it as latest"""
    click.echo(f'importing local file from {file}')
    ctx.local_storage.dataset(name).import_file(file_path=file, tags=parse_tags(tag))


@local_cli.command(name='import')
@click.argument('name')
@click.argument('file')
@click.option('--tag', '-t', default='', help='version tags')
@click.pass_obj
def import_(ctx, name, file, tag):
    """import dataset from file and do not tag"""
    click.echo(f'importing local file from {file}')
    ctx.local_storage.dataset(name).import_file(file_path=file, tags=parse_tags(tag), as_latest=False)


@local_cli.command(name='meta')
@click.argument('name')
@click.option('--version', '-v', help='use this option to select version', default=None)
@click.option('--tag', '-t', help='use this option to select version with tag', default='latest')
@click.pass_obj
def print_meta(ctx, name, version, tag):
    """print metadata of a dataset"""
    dv = _get_dataset_version(ctx, name, version, tag)
    if dv.exists():
        meta = dv.meta()
        if meta:
            click.echo(json.dumps(meta, indent=2))
    else:
        raise BadParameter(f'{dv} do not exists.')


@local_cli.command(name='list-collections')
@click.argument('name')
@click.option('--version', '-v', help='use this option to select version', default=None)
@click.option('--tag', '-t', help='use this option to select version with tag', default='latest')
@click.pass_obj
def list_collections(ctx, name, version, tag):
    """
    list collections of a dataset
    """
    dv = _get_dataset_version(ctx, name, version, tag)
    if dv.exists():
        meta = dv.meta_object()
        click.echo(f'Total collections: {len(meta.collections)}')
        for coll in meta.collections:
            click.echo(coll.name)
    else:
        raise BadParameter(f'{dv} do not exists.')


@local_cli.command(name='code-usage')
@click.argument('name')
@click.option('--collection', '-c', help='collection name', default=DEFAULT_COLLECTION_NAME)
@click.option('--version', '-v', help='use this option to select version', default=None)
@click.option('--tag', '-t', help='use this option to select version with tag', default='latest')
@click.pass_obj
def print_code(ctx, name, collection, version, tag):
    """print data model code of a dataset collection"""
    dv = _get_dataset_version(ctx, name, version, tag)
    if dv.exists():

        if not dv.collection_exists(collection):
            click.echo(f'collection {collection} does not exist. Found the following collection in dataset {name}')
            for c in dv.list_collection_names():
                click.echo(f'  {c}')
            click.echo('---')
            raise BadParameter(f'collection {collection} does not exist.')
        reader_code = get_read_data_code(name, collection, version=version, tag=tag)
        click.echo(reader_code)
    else:
        raise BadParameter(f'{dv} do not exists.')


@local_cli.command(name='print-sample')
@click.argument('name')
@click.option('--collection', '-c', help='collection name', default=DEFAULT_COLLECTION_NAME)
@click.option('--version', '-v', help='use this option to select version', default=None)
@click.option('--tag', '-t', help='use this option to select version with tag', default='latest')
@click.pass_obj
def print_sample(ctx, name, collection, version, tag):
    """print sample content of a dataset collection """
    dv = _get_dataset_version(ctx, name, version, tag)
    if dv.exists():
        if not dv.collection_exists(collection):
            click.echo(f'collection {collection} does not exist. Found the following collection in dataset {name}')
            for c in dv.list_collection_names():
                click.echo(f'  {c}')
            click.echo('---')
            raise BadParameter(f'collection {collection} does not exist.')

        samples = dv.sample(collection)
        click.echo(json.dumps(samples, indent=2))

    else:
        raise BadParameter(f'{dv} do not exists.')


@local_cli.command(name='remove')
@click.argument('name')
@click.option('--force', '-f', default=False, help='Force remove dataset without confirmation.', is_flag=True)
@click.pass_obj
def remove(ctx, name, force):
    """remove all versions of a managed dataset"""
    dataset = ctx.local_storage.dataset(name)
    do_remove = False
    if force:
        do_remove = True
    else:
        confirmation = click.prompt(f'Are you sure you want to remove all versions of dataset {name}? (y/N): ')
        if confirmation.lower() == 'y':
            do_remove = True

    if do_remove:
        dataset.delete()


@local_cli.command(name='remove-version')
@click.argument('name')
@click.option('--version', '-v', help='use this option to select version', default=None)
@click.option('--tag', '-t', help='use this option to select version with tag', default=None)
@click.option('--force', '-f', default=False, help='Force remove dataset without confirmation.', is_flag=True)
@click.pass_obj
def remove_version(ctx, name, version, tag, force):
    """remove a version from a managed dataset"""
    dv = _get_dataset_version(ctx, name, version, tag)
    do_remove = False
    if force:
        do_remove = True
    else:
        confirmation = click.prompt(f'Are you sure you want to remove all versions of dataset {name}? (y/N): ')
        if confirmation.lower() == 'y':
            do_remove = True

    if do_remove:
        dv.delete()


@local_cli.command(name='list')
@click.option('--namespace', '-n', help='select dataset store space to list.', default=None)
@click.pass_obj
def list_datasets(ctx, namespace):
    """list datasets"""
    if namespace:
        items = ctx.local_storage.namespace(namespace).datasets()
    else:
        items = ctx.local_storage.datasets()

    click.echo(f'\nFound {len(items)} datasets:\n')
    items = sorted(items, key=lambda x: f'{x.namespace}/{x.dataset_name}')
    for item in items:
        click.echo(f'  {item.namespace}/{item.dataset_name}')
    click.echo('')


@local_cli.command(name='list-version')
@click.argument('name')
@click.pass_obj
def list_dataset_versions(ctx, name):
    """list dataset versions"""
    dataset = ctx.local_storage.dataset(name)
    versions = dataset.versions()

    click.echo(f'\nFound {len(versions)} versions:\n')
    for item in versions:
        click.echo(f'  {item.version}')
    click.echo('')


@local_cli.command(name='tag')
@click.argument('name')
@click.argument('tag')
@click.argument('version')
@click.pass_obj
def tag_dataset_version(ctx, name, tag, version):
    """Tag dataset version"""
    dataset = ctx.local_storage.dataset(name)
    dataset.set_tag(tag=tag, version=version)


@local_cli.command(name='untag')
@click.argument('name')
@click.argument('tag')
@click.pass_obj
def untag_dataset_version(ctx, name, tag):
    """Remove dataset version tag"""
    dataset = ctx.local_storage.dataset(name)
    dataset.remove_tag(tag)


@local_cli.command(name='tag-info')
@click.argument('name')
@click.argument('tag')
@click.pass_obj
def print_tag_info(ctx, name, tag):
    """Print dataset version tag information"""
    dataset = ctx.local_storage.dataset(name)
    tagged_version = dataset.resolve_tag(tag=tag)
    if tagged_version:
        click.echo(f"{tag} : {tagged_version}")
    else:
        click.echo(f"{tag} do not exists")
