from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class BinaryFile(BaseModel):
    name: str
    source: Optional[str] = None


class DataItemStorageFormat(str, Enum):
    jsonl = 'jsonl'


class CollectionConfig(BaseModel):
    name: str
    data_format: DataItemStorageFormat = DataItemStorageFormat.jsonl


class DatasetFileMeta(BaseModel):
    author: Optional[str] = None
    authorEmail: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    collections: List[CollectionConfig] = Field(default_factory=list)
    dataset_metadata: Optional[Dict[str, str]] = None

    def find_collection(self, name) -> Optional[CollectionConfig]:
        matched_coll = [c for c in self.collections if c.name == name]
        if len(matched_coll) == 0:
            return None
        return matched_coll[0]
