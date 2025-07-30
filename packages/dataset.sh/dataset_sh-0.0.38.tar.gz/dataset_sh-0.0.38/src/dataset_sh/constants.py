import os.path

CONFIG_JSON = os.path.expanduser('~/.dataset_sh_config.json')
DEFAULT_AUTHOR_JSON = os.path.expanduser('~/.dataset_sh_author.json')

STORAGE_BASE = os.path.expanduser('~/dataset_sh/storage')
DAEMON_PID_FILE = os.environ.get(
    'DSH_DAEMON_PID_FILE',
    os.path.expanduser('~/dataset_sh/daemon.pid')
)

DSH_DEFAULT_HOST = os.getenv('DSH_DEFAULT_HOST', 'https://base.dataset.sh')

SAMPLE_CHAR_COUNT = 1000 * 10

DEFAULT_COLLECTION_NAME = 'main'
