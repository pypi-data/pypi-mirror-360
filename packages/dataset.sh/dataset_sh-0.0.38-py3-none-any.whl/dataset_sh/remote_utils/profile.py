import getpass
import os
import json
import warnings
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError
import dataset_sh.constants as DatasetConstants


class DatasetClientProfile(BaseModel):
    host: str
    key: str
    name: Optional[str] = None


class DatasetClientProfileConfig(BaseModel):
    profiles: List[DatasetClientProfile] = Field(default_factory=list)

    @staticmethod
    def load_profiles():
        config_file = DatasetConstants.CONFIG_JSON
        if os.path.exists(config_file):
            with open(config_file) as fd:
                try:
                    json_config = json.load(fd)
                    ret = DatasetClientProfileConfig(**json_config)
                    return ret
                except (ValidationError, json.decoder.JSONDecodeError):
                    warnings.warn('cannot parse profile config')
        return DatasetClientProfileConfig()

    def get_profile(
            self,
            profile_name='default') -> Optional[DatasetClientProfile]:
        for p in self.profiles:
            if p.name == profile_name:
                return p
        return None

    def get_by_host(self, hostname) -> Optional[DatasetClientProfile]:
        for p in self.profiles:
            if p.host == hostname:
                return p
        return None

    def save(self):
        config_file = DatasetConstants.CONFIG_JSON
        data = self.model_dump(mode='json')
        with open(config_file, 'w') as out:
            json.dump(data, out, indent=4)

    def set_profile(self, host, key, name='default'):
        for p in self.profiles:
            if p.name == name:
                p.host = host
                p.key = key
                return self
        self.profiles.append(DatasetClientProfile(host=host, key=key, name=name))
        return self

    def remove_profile(self, name):
        new_profiles = []
        for p in self.profiles:
            if p.name != name:
                new_profiles.append(p)
        self.profiles = new_profiles
        return self

    @staticmethod
    def read_and_resolve(profile_name):
        return DatasetClientProfileConfig.load_profiles().get_profile(profile_name)

    @staticmethod
    def add_and_save(host, key, name='default'):
        return DatasetClientProfileConfig.load_profiles().set_profile(host, key, name).save()


def ask_override():
    c = input(f'Overwrite existing profile? (y/N)').strip()
    if c.lower() == 'y':
        return True
    return False


def ask_hostname(current):
    hostname = input(f'Enter Host Address: (default: {current})').strip()
    if hostname.strip() == '':
        hostname = current
    return hostname


def ask_name(default_name='default'):
    name = input(f'Profile Name: (default: {default_name})').strip()
    if name == '':
        name = default_name
    return name


def ask_access_key(warn_empty=True):
    key = getpass.getpass('Enter your access key (Your input will be hidden): ').strip()
    return key
