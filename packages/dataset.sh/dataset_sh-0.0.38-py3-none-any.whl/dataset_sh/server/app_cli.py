#!/usr/bin/env python3
import click

from dataset_sh.server.app import create_app

from dataset_sh.server.config_cli import config_cli
from dataset_sh.server.core import RepoServerConfig


@click.group(name='dataset-sh-server')
def dsh_server_cli():
    pass


@dsh_server_cli.command(name='start')
@click.option('--host', default='127.0.0.1', help='The interface to bind to.')
@click.option('--port', default=8989, type=int, help='The port to bind to.')
@click.option('--debug', is_flag=True, help='Run the server in debug mode.')
@click.option('--config', default=None, help='location of the dataset.sh server config file.')
def start(host, port, debug, config):
    server_config = None
    if config is not None:
        server_config = RepoServerConfig.load_from_file(config).override_from_env()
    app = create_app(config=server_config)
    app.run(host=host, port=port, debug=debug)


dsh_server_cli.add_command(config_cli)

if __name__ == '__main__':
    dsh_server_cli()
