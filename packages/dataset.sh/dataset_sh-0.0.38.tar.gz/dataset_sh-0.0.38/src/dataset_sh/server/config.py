import json
import os
import warnings

from dataset_sh.server.core import RepoServerConfig


def load_config(app=None) -> RepoServerConfig:
    config_file = os.environ.get('DATASET_SH_SERVER_CONFIG_FILE', './dataset-sh-server-config.json')

    if config_file is None or not os.path.exists(config_file):
        if not os.path.exists(config_file):
            warnings.warn('server config do not exist, server will be using a default configuration file, '
                          'which may affect some functionality, consider create and modify a configuration file.')
        # host = 'localhost'
        # port = '5000'
        # if app is not None:
        #     host = app.config.get('SERVER_NAME', host)
        #     if host is None:
        #         host = '127.0.0.1'
        #     port = app.config.get('SERVER_PORT', port)
        return RepoServerConfig().override_from_env()
    else:
        with open(config_file) as fd:
            return RepoServerConfig(**json.load(fd)).override_from_env()
