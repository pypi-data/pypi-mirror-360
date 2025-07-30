import click

from dataset_sh.clients.locator import DatasetLocator
from dataset_sh.clients.obj import Remote, remote
from dataset_sh.dependency.parser import parse_file


@click.group(name='project')
def project_cli():
    """to manage dataset.sh project"""
    pass


@project_cli.command(name='install')
@click.argument('file_path')
def install_project(file_path):
    """install all datasets listed in project file."""

    dep = parse_file(file_path)
    for host_group in dep.dependencies:
        host = host_group.host
        host_remote = remote(host=host)
        for dataset_item in host_group.datasets:
            source_locator = DatasetLocator.from_str(dataset_item.source)

            target = dataset_item.target
            if target is None:
                target = dataset_item.source

            target_locator = DatasetLocator.from_str(target)
            source_dv = source_locator.resolve_remote(host_remote)
            source_dv.download_to(
                target_locator.resolve_local_dataset()
                ,
                tags=[target_locator.tag]
            )
