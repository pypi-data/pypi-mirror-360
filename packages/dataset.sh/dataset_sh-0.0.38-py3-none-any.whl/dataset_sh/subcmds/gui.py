import threading
import time

import click

from dataset_sh.server.daemon import daemon_is_running, launch_daemon_app


@click.command(name='gui')
@click.argument('dataset', default='')
@click.option('--host', '-h', 'host', help='if daemon is not running, make the daemon listen to this host.',
              default='localhost')
@click.option('--port', '-p', 'port', help='if daemon is not running, run the daemon on this port.', default=48989)
def gui_cli(dataset, host, port):
    """inspect dataset in web-based gui"""
    host_port = daemon_is_running()
    if host_port:
        host, port = host_port
        url = f'http://{host}:{port}/dataset/{dataset}' if dataset != '' else f'http://{host}:{port}'
        click.launch(url)
    else:
        url = f'http://{host}:{port}/dataset/{dataset}' if dataset != '' else f'http://{host}:{port}'

        def open_browser():
            # Wait a few seconds before opening the browser
            time.sleep(1)
            click.launch(url)

        threading.Thread(target=open_browser).start()
        launch_daemon_app(host, port)
