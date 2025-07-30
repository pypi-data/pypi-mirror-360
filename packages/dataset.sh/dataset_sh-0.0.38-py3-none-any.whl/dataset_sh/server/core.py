import json
import os.path
import warnings
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

from dataset_sh.server.auth import decode_key, verify_password, hash_password, encode_key, generate_password


class RepoServerUserProfile(BaseModel):
    user: str
    hashed: str


class RepoServerConfig(BaseModel):
    require_auth: bool = False

    allow_upload: bool = False

    hostname: str = 'http://localhost:5000'
    users: List[RepoServerUserProfile] = Field(default_factory=list)
    secret_key: str = Field(default_factory=generate_password)
    data_folder: str = os.path.expanduser('~/dataset_sh/storage')
    uploader_folder: str = os.path.expanduser('~/dataset_sh/uploader')
    article_folder: str = os.path.expanduser('~/dataset_sh/posts')

    max_chunk_count: int = 500
    minimal_chunk_size: int = 1 * 1024 * 1024

    def override_from_env(self):
        self.data_folder = os.getenv('DSH_APP_STORAGE_DIR', self.data_folder)
        self.uploader_folder = os.getenv('DSH_APP_UPLOADER_DIR', self.uploader_folder)
        self.article_folder = os.getenv('DSH_APP_ARTICLE_DIR', self.article_folder)
        self.hostname = os.getenv('DSH_APP_HOSTNAME', self.hostname)
        # sue a value such as  http://127.0.0.1:5000 to display download section.

        self.max_chunk_count = int(os.getenv('DSH_APP_MAX_CHUNK_COUNT', self.max_chunk_count))
        self.minimal_chunk_size = int(os.getenv('DSH_APP_MINIMAL_CHUNK_SIZE', self.minimal_chunk_size))

        return self

    def make_dirs(self):
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.uploader_folder, exist_ok=True)
        os.makedirs(self.article_folder, exist_ok=True)

    @staticmethod
    def load_from_file(fp):
        try:
            with open(fp, 'r') as fin:
                return RepoServerConfig(**json.load(fin))
        except (FileNotFoundError, json.JSONDecodeError, ValidationError):
            warnings.warn('cannot load server config, using default config now ')
            return RepoServerConfig()

    def write_to_file(self, fp):
        with open(fp, 'w') as out:
            json.dump(self.model_dump(mode='json'), out, indent=4)

    @staticmethod
    def generate_key(username, password):
        return encode_key(username, password)

    def update_password(self, username, password):
        for u in self.users:
            if u.user == username:
                u.hashed = hash_password(password)
                return
        self.users.append(RepoServerUserProfile(
            user=username,
            hashed=hash_password(password)
        ))

    def verify_key(self, key) -> Optional[str]:
        up_or_none = decode_key(key)
        if up_or_none is None:
            return None

        username, password = up_or_none
        if self.verify_userpass(username, password):
            return username
        return None

    def verify_userpass(self, username, password) -> bool:
        u = self.get_user(username)
        if u:
            return verify_password(password, u.hashed)
        else:
            return False

    def get_user(self, username):
        for u in self.users:
            if u.user == username:
                return u
        return None
