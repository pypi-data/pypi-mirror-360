from typing import Optional

from pydantic import BaseModel


#
# class HostAlias(BaseModel):
#     name: str
#     host: str
#
#
# class HostAliasList(BaseModel):
#     aliases: List[HostAlias] = Field(default_factory=list)
#
#     def resolve_alias(self, name) -> Optional[str]:
#         for item in self.aliases:
#             if item.name == name:
#                 return item.host
#         if name == 'default':
#             return DatasetConstants.CENTRAL_HOST
#         return None
#
#     def save(self):
#         config_file = DatasetConstants.ALIAS_FILE
#         data = self.model_dump(mode='json')
#         with open(config_file, 'w') as out:
#             json.dump(data, out, indent=4)
#
#     def add_alias(self, name, host):
#         HostAliasList.is_valid_host_address(host, throw=True)
#         for item in self.aliases:
#             if item.name == name:
#                 item.host = host
#                 return
#         self.aliases.append(HostAlias(name=name, host=host))
#         return self
#
#     def remove_alias(self, name):
#         aliases = []
#         for item in self.aliases:
#             if item.name != name:
#                 aliases.append(item)
#         self.aliases = aliases
#         return self
#
#     @staticmethod
#     def load_from_disk():
#         config_file = DatasetConstants.ALIAS_FILE
#         if os.path.exists(config_file):
#             with open(config_file, 'r') as content:
#                 try:
#                     json_content = json.load(content)
#                     ret = HostAliasList(**json_content)
#                     return ret
#                 except (ValidationError, json.decoder.JSONDecodeError):
#                     warnings.warn('cannot parse profile config')
#         return HostAliasList()
#
#     @staticmethod
#     def resolve_host_or_alias(host: Optional[str]):
#
#         if host is None:
#             host = 'default'
#
#         if '://' in host:
#             return host
#         host_addr = HostAliasList.load_from_disk().resolve_alias(host)
#         if host_addr:
#             if host_addr.startswith('http://') or host_addr.startswith('https://'):
#                 return host_addr
#             else:
#                 raise ValueError(f'Invalid host address: {host_addr}, it must starts with https:// or http://')

# @staticmethod
def is_valid_host_address(host_addr, throw=True):
    if host_addr.startswith('http://') or host_addr.startswith('https://'):
        return True
    else:
        if throw:
            raise ValueError(f'Invalid host address: {host_addr}, it must starts with https:// or http://')
        else:
            return False


class TagResolveResult(BaseModel):
    version: Optional[str] = None
    tag: str


class DatasetVersionEntry(BaseModel):
    version: str
    createdAt: Optional[float] = None
    description: Optional[str] = None
    fileSize: int = None


class ListVersionResult(BaseModel):
    items: list[DatasetVersionEntry]


class ListVersionTagResult(BaseModel):
    items: list[TagResolveResult]


def url_join(base_url, *path_items):
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    return '/'.join([base_url, *path_items])
