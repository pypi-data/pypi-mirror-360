from dataclasses import dataclass

import click
import docker
import os
from datetime import datetime

from dataset_sh import Remote, LocalStorage
from dataset_sh.io import DatasetFileWriter
from dataset_sh.server.core import RepoServerConfig
from dataset_sh.utils.files import checksum
from tests.core.test_io import NameAndCount


def get_default_root_folder():
    """Generate default root folder path with current date."""
    current_date = datetime.now().strftime('%Y_%m_%d')
    return os.path.join('/tmp', 'dataset_sh_sys_testing', f'test_{current_date}')


@dataclass
class DatasetTestingBaseFolder:
    base: str

    @property
    def base_path(self):
        return self.base

    @property
    def server_config(self):
        return os.path.abspath(os.path.join(self.base, 'server.config'))

    @property
    def client_config(self):
        return os.path.abspath(os.path.join(self.base, 'client.config'))

    @property
    def data_dir(self):
        return os.path.abspath(os.path.join(self.base, 'data'))

    @property
    def uploader_dir(self):
        return os.path.abspath(os.path.join(self.base, 'uploader'))

    @property
    def posts_dir(self):
        return os.path.abspath(os.path.join(self.base, 'posts'))

    @property
    def download_dir(self):
        return os.path.abspath(os.path.join(self.base, 'download'))

    @property
    def draft_dir(self):
        return os.path.abspath(os.path.join(self.base, 'drafts'))

    def prepare(self):
        os.makedirs(self.base, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.uploader_dir, exist_ok=True)
        os.makedirs(self.posts_dir, exist_ok=True)
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.draft_dir, exist_ok=True)

    def cleanup(self):
        import shutil
        shutil.rmtree(self.base)


def start_server(
        root_folder: DatasetTestingBaseFolder,
        image_name='dsh-dev-local',
        port=29999,
        container_name='dsh-test-upload',
        mode='debug',
):
    environment = {
        'DSH_APP_HOSTNAME': f'http://localhost:{port}',
    }

    volumes = {
        str(root_folder.data_dir): {
            'bind': '/app/data',
            'mode': 'rw'
        },
        str(root_folder.posts_dir): {
            'bind': '/app/posts',
            'mode': 'rw'
        },
        str(root_folder.uploader_dir): {
            'bind': '/app/uploader',
            'mode': 'rw'
        },
        str(root_folder.server_config): {
            'bind': '/app/dataset-sh-server-config.json',  # exact file path inside container
            'mode': 'ro'  # optional: read-only
        }
    }

    client = docker.from_env()

    cmds = {
        'debug': ['flask', '--app', 'dataset_sh.server.app', 'run', '--debug', '-p', '8989', '-h', '0.0.0.0'],
        'production': ["gunicorn", "-b", "0.0.0.0:8989", "dataset_sh.server.app:create_app()"],
    }

    try:
        container = client.containers.run(
            image_name,
            name=container_name,
            detach=True,
            environment=environment,
            volumes=volumes,
            ports={'8989/tcp': port},
            # network='bridge',
            restart_policy={"Name": "unless-stopped"},
            command=cmds[mode]
        )

        print(f"Container started: {container.id}")

        # Print container logs
        import time
        start_time = time.time()
        timeout = 10  # Wait up to 10 seconds for initial logs

        while time.time() - start_time < timeout:
            logs = container.logs(since=int(start_time))
            if logs:
                print(logs.decode('utf-8').strip())
                break
            time.sleep(1)

        return container

    except docker.errors.APIError as e:
        print(f"Error creating container: {e}")
    except docker.errors.ImageNotFound as e:
        print(f"Image not found: {e}")


def stop_and_remove_container(container_name='dsh-test-upload'):
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)

        # Stop the container
        print(f"Stopping container: {container_name}")
        container.stop(timeout=10)  # wait up to 10 seconds for graceful stop

        # Remove the container
        print(f"Removing container: {container_name}")
        container.remove()

        print(f"Container {container_name} has been stopped and removed")

    except docker.errors.NotFound:
        print(f"Container {container_name} not found")
    except docker.errors.APIError as e:
        print(f"Error while stopping/removing container: {e}")


def is_same_file(f1, f2):
    return checksum(f1) == checksum(f2)


def run_all(root_dir: DatasetTestingBaseFolder):
    """

    1. start server
        1. create config with an user key
        2. mount to config to server container
        3. run container
    2. create draft dataset
    3. upload data to draft dataset
        1. check if data is uploaded
    4. download data from draft dataset
        1. check if data is downloaded

    """
    # 1. start server

    root_dir.cleanup()
    root_dir.prepare()

    port = 8989

    username = 'test-user'
    password = 'test-password'
    host = f'http://localhost:{port}'

    # create config with an user key
    repo_config = RepoServerConfig()
    repo_config.update_password(username, password)
    repo_config.allow_upload = True
    repo_config.minimal_chunk_size = 5 * 1024 * 1024

    repo_config.write_to_file(root_dir.server_config)

    access_key = repo_config.generate_key(username, password)

    #         3. run container
    stop_and_remove_container()
    start_server(root_dir, port=port)

    dataset_file = os.path.join(root_dir.draft_dir, 'test-upload.dataset')

    #     2. create draft dataset
    with DatasetFileWriter(dataset_file) as writer:
        writer.add_collection('main', [
            NameAndCount('a', i).to_dict() for i in range(100)
        ])

        random_data = os.urandom(15 * 1024 * 1024)

        writer.add_binary_file('fake.data', random_data)

    version = checksum(dataset_file)
    print(f'Dataset version: {version}')

    # upload
    remote = Remote(host=host, access_key=access_key)
    remote.dataset('test-user/test-upload').upload_from_file(dataset_file, ['latest'])

    # download
    dd = LocalStorage(root_dir.data_dir).dataset('test/test-download')
    dd.import_file(dataset_file)


if __name__ == '__main__':
    root_dir = DatasetTestingBaseFolder('/tmp/dsh-test')
