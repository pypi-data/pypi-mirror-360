import abc
import os
from typing import Optional
from importlib.metadata import version as lib_version

import requests


class MarkedFolder:
    location: str
    parent: Optional['MarkedFolder']

    def __init__(self, location, parent=None):
        self.location = location
        self.parent = parent

    @abc.abstractmethod
    def marker_file(self) -> str:
        raise NotImplementedError()

    def post_create(self):
        return

    def exists(self):
        """
        this marked folder exists iff its marker file exist.
        Returns:

        """
        return os.path.isfile(self.marker_file())

    def create_location(self):
        os.makedirs(self.location, exist_ok=True)

    def create(self):
        self.create_location()
        if not self.exists():
            with open(self.marker_file(), 'w') as out:
                out.write('1')
            self.post_create()
        if self.parent and not self.parent.exists():
            self.parent.create()

    def create_if_not_exists(self):
        if not self.exists():
            self.create()


def version_check(remote_server_url):
    """
    check dataset.sh version of a remote server.
    Returns:

    """
    local_version = lib_version('dataset.sh')
    ping_url = remote_server_url
    api_url = url_join(self.remote.host, 'api', 'info')
    headers = self.remote.get_headers()
    resp = requests.get(
        api_url,
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def compare_version(local_version, remote_version):
    pass
