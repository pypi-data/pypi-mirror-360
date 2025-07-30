import json

import click

from dataset_sh import open_dataset_file
from dataset_sh.constants import DEFAULT_COLLECTION_NAME
from dataset_sh.typing.codegen import CodeGenerator


@click.group(name='file')
def file_cli():
    """to interact with standalone dataset.sh file"""
    pass


@file_cli.command(name='list-collections')
@click.argument('filepath', type=click.Path())
def list_collections(filepath):
    """list collections of a dataset file"""
    with open_dataset_file(filepath) as reader:
        collections = reader.collections()
        click.echo(f'Total collections: {len(collections)}')
        for coll in collections:
            click.echo(coll)


@file_cli.command(name='print-code')
@click.argument('filepath', type=click.Path())
@click.argument('collection_name')
def print_code(filepath, collection_name):
    """print usage code of the given collection on the dataset file"""
    with open_dataset_file(filepath) as reader:
        coll = reader.collection(collection_name)
        loader_code = CodeGenerator.generate_file_loader_code(filepath, collection_name)
        click.echo(loader_code)


@file_cli.command(name='print-sample')
@click.argument('filepath', type=click.Path())
@click.option('--collection', '-c', help='collection name', default=DEFAULT_COLLECTION_NAME)
def print_sample(filepath, collection):
    """print data samples of the given collection on a dataset file"""
    with open_dataset_file(filepath) as reader:
        sample = reader.collection(collection).top()
        click.echo(json.dumps(sample, indent=2))
