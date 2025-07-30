from __future__ import annotations
import json
import os.path
import shutil
import tempfile
import uuid
import warnings
from typing import Optional, List

import requests
from easytype.core import UserDefinedType

from dataset_sh import DatasetFile, open_dataset_file
from dataset_sh.clients.common import MarkedFolder
from dataset_sh.clients.remote import url_join, TagResolveResult, ListVersionResult, ListVersionTagResult

from dataset_sh.core import DatasetFileMeta
from dataset_sh.fileserver.client import FileServerClient
from dataset_sh.models import DatasetFileInternalPath
from dataset_sh.multipart.upload import upload_to_url
from dataset_sh.remote_utils.profile import DatasetClientProfileConfig
from dataset_sh.utils.files import checksum, download_url
from dataset_sh.utils.misc import parse_dataset_name, read_jsonl, compare_version
from dataset_sh.utils.dump import dump_collections, dump_single_collection

import dataset_sh.constants as DatasetConstants
from dataset_sh.utils.usage.read_data_codegen import get_read_data_code


class LocalDatasetVersion(MarkedFolder):
    location: str
    namespace: str
    dataset_name: str
    version: str

    def __init__(self, location, parent, namespace, dataset_name, version):
        super().__init__(location, parent)
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.version = version

    def __eq__(self, other):
        return self.namespace == other.namespace and self.dataset_name == other.dataset_name and self.version == other.version

    def open(self):
        return DatasetFile.open(self.datafile(), 'r')

    # Filepaths
    def marker_file(self) -> str:
        return os.path.join(self.location, '.dataset.version.marker')

    def datafile(self):
        return os.path.join(self.location, 'file')

    def metafile(self):
        return os.path.join(self.location, 'meta.json')

    # def code_example_file(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME):
    #     return os.path.join(self.location, f'usage_code_{collection_name}.py')

    def sample_file(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME):
        return os.path.join(self.location, f'data_sample_{collection_name}.jsonl')

    def type_annotation_file(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME):
        return os.path.join(self.location, f'type_annotation_{collection_name}.json')

    # End of Filepaths

    def __repr__(self):
        return f'{self.namespace}/{self.dataset_name}:version={self.version}'

    def __str__(self):
        return f'{self.namespace}/{self.dataset_name}:version={self.version}'

    def meta(self) -> DatasetFileMeta | dict:
        with open(self.metafile()) as fd:
            return json.load(fd)

    def meta_object(self) -> DatasetFileMeta:
        return DatasetFileMeta(**self.meta())

    def type_annotation_dict(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME):
        if os.path.isfile(self.type_annotation_file(collection_name)):
            with open(self.type_annotation_file(collection_name)) as fd:
                return json.load(fd)
        return None

    def sample(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME):
        if os.path.isfile(self.sample_file(collection_name)):
            with open(self.sample_file(collection_name)) as fd:
                return list(read_jsonl(fd))
        return []

    def list_collection_names(self):
        meta = self.meta()
        meta = DatasetFileMeta(**meta)
        for c in meta.collections:
            yield c.name

    def collection_exists(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME) -> bool:
        meta = self.meta()
        meta = DatasetFileMeta(**meta)
        for c in meta.collections:
            if c.name == collection_name:
                return True
        return False

    def usage_code(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME):
        meta = self.meta()
        meta = DatasetFileMeta(**meta)
        cs = [c for c in meta.collections if c.name == collection_name]
        if len(cs) > 0:
            reader_code = get_read_data_code(
                f'{self.namespace}/{self.dataset_name}',
                collection_name,
                version=self.version,
                tag=None
            )
            return reader_code
        else:
            return ''

    # def model_entry_point(self, collection_name=DatasetConstants.DEFAULT_COLLECTION_NAME) -> Optional[str]:
    #     meta = self.meta()
    #     meta = DatasetFileMeta(**meta)
    #     cs = [c for c in meta.collections if c.name == collection_name]
    #     if len(cs) > 0:
    #         return cs[0].data_schema.entry_point
    #     else:
    #         return None

    def delete(self):
        shutil.rmtree(self.location)

    def upload_to(self, dest: 'RemoteDataset' = None, tags: Optional[List[str]] = None):
        if dest is None:
            dest = remote().namespace(self.namespace).dataset(self.dataset_name)
        dest.upload_from_local(self, tags=tags)

    def upload_as_latest_to(self, dest: 'RemoteDataset' = None):
        if dest is None:
            dest = remote().namespace(self.namespace).dataset(self.dataset_name)
        dest.upload_from_local(self, tags=['latest'])

    def extract_sample_and_code_usage(self):
        with open_dataset_file(self.datafile()) as reader:
            meta_file_dest = self.metafile()
            with reader.zip_file.open(DatasetFileInternalPath.META_FILE_NAME, 'r') as fd:
                with open(meta_file_dest, 'wb') as out:
                    out.write(fd.read())

            for coll_name in reader.collections():
                coll = reader.collection(coll_name)
                with open(self.sample_file(coll_name), 'w') as out:
                    # samples = coll.top(n=10)
                    char_wrote = 0
                    line_count = 0
                    for item in coll:
                        if char_wrote > DatasetConstants.SAMPLE_CHAR_COUNT or line_count > 30:
                            break
                        line = json.dumps(item)
                        char_wrote += len(line)
                        line_count += 1
                        out.write(f'{line}\n')

                with open(self.type_annotation_file(coll_name), 'w') as out:
                    type_annotation_dict = coll.type_annotation_dict()
                    out.write(
                        json.dumps(type_annotation_dict)
                    )
                # with open(self.code_example_file(coll_name), 'w') as out:
                #     code = coll.code_usage()
                #     out.write(code)


class LocalDataset(MarkedFolder):
    location: str
    namespace: str
    dataset_name: str

    def __init__(self, location, parent, namespace, dataset_name):
        super().__init__(location, parent)
        self.namespace = namespace
        self.dataset_name = dataset_name

    def __eq__(self, other):
        return self.namespace == other.namespace and self.dataset_name == other.dataset_name

    def readme(self):
        if os.path.exists(self.readme_file()):
            with open(self.readme_file()) as fd:
                return fd.read()
        return None

    def set_readme(self, content):
        os.makedirs(os.path.dirname(self.readme_file()), exist_ok=True)
        with open(self.readme_file(), 'w') as fd:
            fd.write(content)

    def delete(self):
        shutil.rmtree(self.location)

    def post_create(self):
        os.makedirs(os.path.join(self.location, 'version'), exist_ok=True)

    def marker_file(self):
        return os.path.join(self.location, '.dataset.marker')

    def version_folder(self):
        return os.path.join(self.location, 'version')

    def tag_file(self):
        return os.path.join(self.location, 'tag')

    def readme_file(self):
        return os.path.join(self.location, 'readme.md')

    def read_tag_file(self):
        if os.path.exists(self.tag_file()):
            with open(self.tag_file()) as fd:
                return json.load(fd)
        else:
            return {"tags": {}}

    def save_tag_file(self, tags):
        with open(self.tag_file(), 'w') as fd:
            json.dump(tags, fd)
        return self

    def set_tag(self, tag: str, version: str):
        tags = self.read_tag_file()
        tags['tags'][tag] = version
        self.save_tag_file(tags)
        return self

    def remove_tag(self, tag):
        tags = self.read_tag_file()
        del tags['tags'][tag]
        self.save_tag_file(tags)
        return self

    def resolve_tag(self, tag) -> Optional[str]:
        tags = self.read_tag_file()
        return tags['tags'].get(tag, None)

    def versions(self) -> list[LocalDatasetVersion]:
        items = []
        for version_id in os.listdir(self.version_folder()):
            v = self.version(version_id)
            if v.exists():
                items.append(v)
        return items

    def version(self, version_id) -> LocalDatasetVersion:
        version_location = os.path.join(self.location, 'version', version_id)
        return LocalDatasetVersion(version_location, self, self.namespace, self.dataset_name, version_id)

    def tags(self):
        tags = self.read_tag_file()
        return tags['tags']

    def tag(self, tag, allow_none=False) -> LocalDatasetVersion | None:
        version = self.resolve_tag(tag)
        if version is None:
            if allow_none:
                return None
            else:
                raise ValueError('tag do not exist.')
        return self.version(version)

    def latest(self) -> LocalDatasetVersion | None:
        return self.tag('latest')

    def open(self):
        return self.latest().open()

    def import_file(
            self,
            file_path,
            replace=False,
            remove_source=False,
            verify_version: Optional[str] = None,
            tags: Optional[List[str]] = None,
            as_latest=True
    ) -> LocalDatasetVersion | None:
        """
        create a new version from a dataset file.
        Args:
            file_path:
            replace: replace existing version with new version.
            remove_source: delete source file after successful import.
            verify_version: make sure the imported version checksum match the given value.
            tags: tag the version after  successful import.
            as_latest: tag the newly imported version as latest.

        Returns:

        """
        new_version_id = checksum(file_path)

        if verify_version and verify_version != new_version_id:
            raise ValueError('provided version do not match file signature.')
        new_version = self.version(new_version_id)
        if new_version.exists():
            if not replace:
                warnings.warn(f'dataset {self.namespace}/{self.dataset_name} version {new_version_id} already exists')
                return

        new_version_folder = new_version
        os.makedirs(
            new_version_folder.location, exist_ok=False
        )

        if remove_source:
            shutil.move(file_path, new_version_folder.datafile())
        else:
            shutil.copy2(file_path, new_version_folder.datafile())

        new_version.create()
        new_version.extract_sample_and_code_usage()
        if tags:
            for t in tags:
                self.set_tag(t, new_version_id)

        if as_latest:
            self.set_tag('latest', new_version_id)

        return new_version

    def import_data(
            self,
            collections,
            type_dict=None,
            tags: Optional[List[str]] = None,
            description: Optional[str] = None,
            as_latest=True,
            load_author=True
    ):
        """

        Args:
            collections:      data for each collection, dict key is collection name, value is collection data.
            type_dict:        type annotation for each collection, dict key is collection name, value is type annotation.
            tags:             tag this version.
            description:      describe this version.
            as_latest:        tag this version as latest.
            load_author:      load stored author information, you can use command `dataset.sh author` to display and modify author information.

        Returns:

        """
        with tempfile.TemporaryDirectory() as td:
            temp_dataset_file = os.path.join(td, 'temp.dataset')
            dump_collections(
                temp_dataset_file,
                collections,
                type_dict=type_dict,
                description=description,
                load_author=load_author
            )
            return self.import_file(temp_dataset_file, tags=tags, as_latest=as_latest)

    def import_collection(
            self,
            collection,
            name=DatasetConstants.DEFAULT_COLLECTION_NAME,
            type_annotation: Optional[UserDefinedType] = None,
            tags: Optional[List[str]] = None,
            description: Optional[str] = None,
            as_latest=True,
            load_author=True
    ):
        """

        Args:
            collection:       data of the collection.
            name:             name of the collection, default to `dataset_sh.constants.DEFAULT_COLLECTION_NAME`
            type_annotation:  type annotation for the collection.
            tags:             tag this version.
            description:      describe this version.
            as_latest:        tag this version as latest.
            load_author:      load stored author information, you can use command `dataset.sh author` to display and modify author information.

        Returns:

        """
        with tempfile.TemporaryDirectory() as td:
            temp_dataset_file = os.path.join(td, 'temp.dataset')
            dump_single_collection(
                temp_dataset_file,
                collection,
                name=name,
                type_annotation=type_annotation,
                description=description,
                load_author=load_author
            )
            return self.import_file(temp_dataset_file, tags=tags, as_latest=as_latest)

    def __repr__(self):
        return f'{self.namespace}/{self.dataset_name}'

    def __str__(self):
        return f'{self.namespace}/{self.dataset_name}'


class LocalNamespace(MarkedFolder):
    location: str
    namespace: str

    def __init__(self, location, parent, namespace):
        super().__init__(location, parent)
        self.namespace = namespace

    def __eq__(self, other):
        return self.namespace == other.namespace

    def marker_file(self):
        return os.path.join(self.location, '.dataset.namespace.marker')

    def datasets(self) -> list[LocalDataset]:
        datasets = []
        if os.path.exists(self.location):
            for dataset_name in os.listdir(self.location):
                if self.dataset(dataset_name).exists():
                    datasets.append(self.dataset(dataset_name))
        return datasets

    def dataset(self, dataset_name) -> LocalDataset:
        loc = os.path.join(self.location, dataset_name)
        return LocalDataset(loc, self, self.namespace, dataset_name)

    def __repr__(self):
        return f'Dataset Namespace: {self.namespace}'

    def __str__(self):
        return f'Dataset Namespace: {self.namespace}'


class LocalStorage(object):
    location: str

    def __init__(self, location=None):
        if location is None:
            location = DatasetConstants.STORAGE_BASE
        self.location = location
        os.makedirs(self.location, exist_ok=True)

    def namespaces(self) -> list[LocalNamespace]:
        namespaces = []
        if os.path.exists(self.location):
            for namespace in os.listdir(self.location):
                if self.namespace(namespace).exists():
                    namespaces.append(self.namespace(namespace))
        return namespaces

    def namespace(self, name) -> LocalNamespace:
        loc = os.path.join(
            self.location,
            name,
        )
        return LocalNamespace(loc, parent=None, namespace=name)

    def datasets(self) -> list[LocalDataset]:
        datasets = []
        for namespace in self.namespaces():
            for d in namespace.datasets():
                datasets.append(d)
        return datasets

    def dataset(self, name) -> LocalDataset:
        username, dataset_name = parse_dataset_name(name)
        return self.namespace(username).dataset(dataset_name)


class RemoteInfo:
    host: str
    access_key: Optional[str]

    def __init__(self, host, access_key=None):
        self.host = host
        self.access_key = access_key

    def get_headers(self):
        if self.access_key:
            return {"X-DATASET-SH-ACCESS-KEY": self.access_key}
        return None

    def get_remote_version(self):
        """
        try get remote server version.
        Returns:

        """
        api_url = url_join(self.host, 'api', 'version')
        r = requests.get(api_url)
        if r.status_code != 200:
            return None
        return r.json()['version']


class RemoteDatasetVersionTag(object):
    remote: RemoteInfo

    namespace: str
    dataset_name: str
    tag: str

    def __init__(self, remote, namespace, dataset_name, tag):
        self.remote = remote
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.tag = tag

    def __repr__(self):
        return f'{self.namespace}/{self.dataset_name}:{self.tag} at {self.remote.host}'

    def _get_download_url(self) -> str:
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'tag', self.tag,
                           'file')
        return api_url

    def download_to_file(self, filepath: str):
        url = self._get_download_url()
        download_url(url, filepath, self.remote.get_headers())

    def download_to(self, dest: LocalDataset, keep_tag=True, additional_tags: Optional[List[str]] = None):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, str(uuid.uuid4()))
            self.download_to_file(temp_file_path)
            version = dest.import_file(temp_file_path, remove_source=True)
            if version:
                if additional_tags:
                    for tag in additional_tags:
                        dest.set_tag(tag, version.version)
                if keep_tag:
                    dest.set_tag(self.tag, version.version)

    def download(self):
        self.download_to(LocalStorage().namespace(self.namespace).dataset(self.dataset_name), keep_tag=True)


class RemoteDatasetVersion(object):
    remote: RemoteInfo

    namespace: str
    dataset_name: str
    version: str

    def __init__(self, remote, namespace, dataset_name, version):
        self.remote = remote
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.version = version

    def __repr__(self):
        return f'{self.namespace}/{self.dataset_name}:{self.version} at {self.remote.host}'

    def _get_download_url(self) -> str:
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'version',
                           self.version,
                           'file')
        return api_url

    def download_to_file(self, filepath: str):
        url = self._get_download_url()
        download_url(url, filepath, self.remote.get_headers())

    def download_to(self, dest: LocalDataset, tags: Optional[List[str]] = None):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, str(uuid.uuid4()))
            self.download_to_file(temp_file_path)
            dest.import_file(temp_file_path, remove_source=True, verify_version=self.version)
            if tags:
                for tag in tags:
                    dest.set_tag(tag, self.version)

    def download(self):
        self.download_to(LocalStorage().namespace(self.namespace).dataset(self.dataset_name))


class RemoteDataset(object):
    remote: RemoteInfo

    namespace: str
    dataset_name: str

    def __init__(self, remote, namespace, dataset_name):
        self.remote = remote
        self.namespace = namespace
        self.dataset_name = dataset_name

    def __repr__(self):
        return f'{self.namespace}/{self.dataset_name} at {self.remote.host}'

    def update_readme(self, readme):
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'readme')
        headers = self.remote.get_headers()
        resp = requests.post(
            api_url,
            headers=headers,
            json={'readme': readme},
        )
        resp.raise_for_status()

    def get_readme(self, readme):
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'readme')
        headers = self.remote.get_headers()
        resp = requests.get(
            api_url,
            headers=headers,
        )
        resp.raise_for_status()
        return resp.text

    def _get_upload_url(self) -> str:
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name)
        return api_url

    def resolve_tag(self, tag):
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'tag', tag)
        headers = self.remote.get_headers()
        resp = requests.get(
            api_url,
            headers=headers,
        )
        resp.raise_for_status()
        return TagResolveResult(**resp.json())

    def tags(self) -> ListVersionResult:
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'tag')
        headers = self.remote.get_headers()
        resp = requests.get(
            api_url,
            headers=headers,
        )
        resp.raise_for_status()
        return ListVersionTagResult(**resp.json())

    def versions(self) -> ListVersionResult:
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'version')
        headers = self.remote.get_headers()
        resp = requests.get(
            api_url,
            headers=headers,
        )
        resp.raise_for_status()
        return ListVersionResult(**resp.json())

    def version(self, version_id) -> RemoteDatasetVersion:
        return RemoteDatasetVersion(self.remote, self.namespace, self.dataset_name, version_id)

    def tag(self, tag) -> RemoteDatasetVersionTag:
        return RemoteDatasetVersionTag(self.remote, self.namespace, self.dataset_name, tag)

    def latest(self) -> RemoteDatasetVersionTag:
        return self.tag('latest')

    def set_tag(self, tag, version):
        api_url = url_join(self.remote.host, 'api', 'dataset', self.namespace, self.dataset_name, 'tag', tag)
        headers = self.remote.get_headers()

        resp = requests.post(
            api_url,
            json={'version': version},
            headers=headers,
        )
        resp.raise_for_status()

    def upload_from_file(self, filepath, tags: Optional[List[str]] = None):
        upload_url = self._get_upload_url()
        params = None

        if tags:
            if params is None:
                params = {}
            params['tag'] = ','.join(tags)
        remote_version = self.remote.get_remote_version()

        if remote_version and compare_version(remote_version, '>=', '0.0.37'):
            resource_url = url_join(self.remote.host, 'api', 'resource')
            upload_client = FileServerClient(resource_url, headers=self.remote.get_headers())
            upload_client.upload(
                filepath,
                self.namespace,
                self.dataset_name,
                tags
            )
        else:
            upload_to_url(
                upload_url,
                filepath,
                self.remote.get_headers(),
                params,
                f'{self.namespace}/{self.dataset_name}'
            )

    def upload_from_local(self, source: LocalDatasetVersion, tags: Optional[List[str]] = None):
        self.upload_from_file(source.datafile(), tags=tags)


class RemoteNamespace(object):
    remote: RemoteInfo
    namespace: str

    def __init__(self, remote, namespace):
        self.remote = remote
        self.namespace = namespace

    def dataset(self, dataset_name) -> RemoteDataset:
        return RemoteDataset(self.remote, self.namespace, dataset_name)

    def __repr__(self):
        return f'namespace {self.namespace} at {self.remote.host}'


class Remote(object):
    remote: RemoteInfo

    def __init__(self, host=None, access_key=None):
        if host is None:
            host = DatasetConstants.DSH_DEFAULT_HOST
        self.remote = RemoteInfo(host, access_key)

    def namespace(self, name) -> RemoteNamespace:
        return RemoteNamespace(self.remote, name)

    def dataset(self, name) -> RemoteDataset:
        username, dataset_name = parse_dataset_name(name)
        return RemoteDataset(self.remote, username, dataset_name)

    def test_connection(self):
        api_url = url_join(self.remote.host, 'api', 'info')
        headers = self.remote.get_headers()
        resp = requests.get(
            api_url,
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()

    def __repr__(self):
        return f'dataset.sh remote server at {self.remote.host}'


def remote(host=None, profile=None, find_profile=True):
    """
    Create remote server based on:
        * host and find_profile
        * profile

    If profile is provided, dataset.sh will connect using the selected profile configuration.

    If host is provided:
        dataset.sh will connect to the given host address,
        and if find_profile is True, the first profile matching the given host url will be used.

    If nothing is provided,
        dataset.sh will connect using default profile, and if default profile is missing, it will connect to
        the default host as a visitor.

    Args:
        host:
        profile:
        find_profile:

    Returns:

    """
    if host is not None:
        if find_profile:
            profile = DatasetClientProfileConfig.load_profiles().get_by_host(host)
            if profile:
                return Remote(host, profile.key)
        return Remote(host)
    elif profile is not None:
        profile = DatasetClientProfileConfig.load_profiles().get_profile(profile_name=profile)
        return Remote(profile.host, profile.key)
    else:
        default_profile = DatasetClientProfileConfig.load_profiles().get_profile(profile_name='default')
        if default_profile is not None:
            return Remote(default_profile.host, default_profile.key)

        return Remote(DatasetConstants.DSH_DEFAULT_HOST)


def dataset(name):
    return LocalStorage().dataset(name)
