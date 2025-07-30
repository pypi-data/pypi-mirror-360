import json
import os

from typing import Optional

import requests

from dataset_sh.constants import DAEMON_PID_FILE
from dataset_sh.server.app import create_app, load_frontend_assets


def save_pid(host: str, port: int, pid: int = None):
    if pid is None:
        pid = os.getpid()

    os.makedirs(os.path.dirname(DAEMON_PID_FILE), exist_ok=True)
    with open(DAEMON_PID_FILE, 'w') as fd:
        daemon_log = {
            'pid': pid,
            'host': host,
            'port': port,
        }
        print(daemon_log)
        json.dump(daemon_log, fd)


def get_running_server_port() -> Optional[tuple[str, int]]:
    if os.path.exists(DAEMON_PID_FILE):
        with open(DAEMON_PID_FILE) as fd:
            try:
                data = json.load(fd)
                host = data['host']
                port = data['port']
                return host, port
            except json.decoder.JSONDecodeError:
                pass
    return None


def daemon_is_running():
    host_port = get_running_server_port()
    if host_port:
        host, port = host_port
        try:
            resp = requests.get(f'http://{host}:{port}/api/version')
            resp.raise_for_status()
            resp_body = resp.json()
            if 'version' in resp_body:
                if resp_body['server'] == 'dataset.sh server':
                    return host, port
        except requests.exceptions.ConnectionError:
            pass

    return None


def launch_daemon_app(host, port) -> Optional[int]:
    _frontend_assets = load_frontend_assets()
    app = create_app(frontend_assets=_frontend_assets)
    save_pid(host, port)
    app.run(port=port, host=host)
