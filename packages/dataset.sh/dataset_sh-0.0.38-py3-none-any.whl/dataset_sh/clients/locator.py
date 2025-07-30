from typing import Optional, Union
from urllib.parse import urlencode

from dataset_sh.clients.obj import Remote, LocalStorage, LocalDatasetVersion, RemoteDatasetVersion, \
    RemoteDatasetVersionTag, RemoteDataset, LocalDataset


class DatasetLocator:
    namespace: str
    dataset_name: str
    tag: Optional[str] = None
    version: Optional[str] = None

    def __init__(self, namespace: str, dataset_name: str, tag: Optional[str] = None, version: Optional[str] = None):
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.tag = tag
        self.version = version

    @staticmethod
    def from_str(str_value) -> 'DatasetLocator':
        """
        DatasetLocator accept the following locator format:
        1. [namespace]/[dataset_name]
            this will be interpreted as [namespace]/[dataset_name]:tag=latest
        2. [namespace]/[dataset_name]:version=[version]
        3. [namespace]/[dataset_name]:tag=[tag_name]

        Args:
            str_value: The string representation of the dataset locator.

        Returns: An instance of DatasetLocator.

        Raises:
            ValueError: If the provided string is not in a valid format.
        """
        parts = str_value.split(':')
        namespace_dataset = parts[0].split('/')
        if len(namespace_dataset) != 2:
            raise ValueError("Invalid format. Must be in the format [namespace]/[dataset_name]")

        namespace, dataset_name = namespace_dataset

        if len(parts) == 1:
            return DatasetLocator(namespace, dataset_name, tag="latest")
        elif len(parts) == 2:
            option, value = parts[1].split('=')
            if option == 'version':
                return DatasetLocator(namespace, dataset_name, version=value)
            elif option == 'tag':
                return DatasetLocator(namespace, dataset_name, tag=value)
            else:
                raise ValueError("Invalid option. Must be 'version' or 'tag'")
        else:
            raise ValueError("Invalid format")

    def resolve_local(self) -> LocalDatasetVersion:
        dataset = LocalStorage().namespace(self.namespace).dataset(self.dataset_name)
        if self.version:
            dv = dataset.version(self.version)
        elif self.tag:
            dv = dataset.tag(self.tag)
        else:
            dv = dataset.latest()
        return dv

    def resolve_remote(self, remote: Remote) -> Union[RemoteDatasetVersion, RemoteDatasetVersionTag]:
        dataset = remote.namespace(self.namespace).dataset(self.dataset_name)
        if self.version:
            dv = dataset.version(self.version)
        elif self.tag:
            dv = dataset.tag(self.tag)
        else:
            dv = dataset.latest()
        return dv

    def resolve_local_dataset(self) -> LocalDataset:
        dataset = LocalStorage().namespace(self.namespace).dataset(self.dataset_name)
        return dataset

    def resolve_remote_dataset(self, remote: Remote) -> RemoteDataset:
        dataset = remote.namespace(self.namespace).dataset(self.dataset_name)
        return dataset

