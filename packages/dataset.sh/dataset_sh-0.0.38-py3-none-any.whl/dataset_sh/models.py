import datetime
from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel, Field


@dataclass
class DatasetInfo:
    name: str
    is_redirect: bool


class DatasetInfoSnippet(BaseModel):
    namespace: str
    dataset: str


class NamespaceList(BaseModel):
    namespaces: List[str]


class DatasetListingResults(BaseModel):
    items: List[DatasetInfoSnippet]


class SourceInfo(BaseModel):
    url: str
    download_time: datetime.datetime = Field(default_factory=datetime.datetime.now)


class DatasetFileInternalPath:
    BINARY_FOLDER = 'bin'
    COLLECTION_FOLDER = 'coll'

    META_FILE_NAME = 'meta.json'
    DATA_FILE = 'data.jsonl'
    TYPE_FILE = 'type.json'


@dataclass
class DatasetSource:
    username: str
    dataset_name: str
    tag: Optional[str]
    version: str

    location: str
