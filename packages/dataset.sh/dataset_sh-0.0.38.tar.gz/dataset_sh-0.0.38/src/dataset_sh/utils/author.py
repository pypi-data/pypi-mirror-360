import json
import os
from typing import Optional

from dataset_sh.constants import DEFAULT_AUTHOR_JSON


def load_author_profile(author_cfg_path=None) -> Optional[dict]:
    if author_cfg_path is None:
        author_cfg_path = DEFAULT_AUTHOR_JSON
    if os.path.exists(author_cfg_path):
        with open(author_cfg_path) as f:
            return json.load(f)
    else:
        return None


def save_author_profile(author, author_email, author_cfg_path=None):
    if author_cfg_path is None:
        author_cfg_path = DEFAULT_AUTHOR_JSON
    with open(author_cfg_path, 'w') as f:
        json.dump(dict(
            author=author,
            author_email=author_email,
        ), f)
