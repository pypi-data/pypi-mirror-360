from typing import List, Optional
from pydantic import BaseModel, Field


class DatasetDependencyItem(BaseModel):
    """
    e.g.
        * user/dataset
        * user/dataset:tag=latest
        * user/dataset:
        * user/dataset
        * user/dataset
    Both source and target should be able to parsed by a DatasetLocator.
    """
    source: str
    target: Optional[str] = None


class DatasetDependencyHostGroup(BaseModel):
    host: str
    datasets: List[DatasetDependencyItem] = Field(default_factory=list)


class DatasetDependencies(BaseModel):
    dependencies: List[DatasetDependencyHostGroup] = Field(default_factory=list)
