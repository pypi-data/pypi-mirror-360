import json
import os
import tempfile
import zipfile
from typing import Optional, List, Union

from easytype.core import UserDefinedType, parse_from_dict, ResolvedType

from .core import CollectionConfig, DatasetFileMeta
from .models import DatasetFileInternalPath
from .utils.misc import id_function
from .utils.sample import reservoir_sampling


class DatasetFile:

    def __init__(self):
        raise ValueError('Please use DatasetFile.open(filename, mode)')

    @staticmethod
    def open(fp: str, mode: str = 'r'):
        """
        Open a dataset file
        :param fp: path to the file
        :param mode: r for read and w for write.
        :return:
        """
        if mode == 'r':
            return DatasetFileReader(fp)
        elif mode == 'w':
            return DatasetFileWriter(fp)
        else:
            raise ValueError('mode must be one of "r" or "w"')

    @staticmethod
    def binary_file_path(fn: str):
        return os.path.join(DatasetFileInternalPath.BINARY_FOLDER, fn)


class DatasetFileWriter:
    def __init__(self, file_path: str, compression=zipfile.ZIP_DEFLATED, compresslevel=9, zip_args=None):
        """
        Write to a dataset file, this object can also be used as a context manager.

        This object need to be closed.

        :param file_path: location of the dataset file to write.
        :param compression: compress mode for zip file.
        :param compresslevel: note that the default compression algorithm ZIP_LZMA do not use this value.

        """
        if zip_args is None:
            zip_args = {}
        self.zip_file = zipfile.ZipFile(
            file_path, 'w', compression=compression, compresslevel=compresslevel,
            **zip_args
        )
        self.meta = DatasetFileMeta()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        close the writer.
        :return:
        """
        with self.zip_file.open(DatasetFileInternalPath.META_FILE_NAME, 'w') as out:
            out.write(self.meta.model_dump_json().encode('utf-8'))
        self.zip_file.close()

    def update_meta(self, meta):
        author = meta.get('author', None)
        if author is not None:
            self.meta.author = author

        author_email = meta.get('authorEmail', None)
        if author_email is not None:
            self.meta.authorEmail = author_email

        tags = meta.get('tags', None)
        if tags is not None:
            self.meta.tags = tags

        dataset_metadata = meta.get('dataset_metadata', None)
        if dataset_metadata is not None:
            self.meta.dataset_metadata = dataset_metadata

    def add_collection(
            self,
            collection_name: str,
            data: List[Union[dict, list]],
            type_annotation: Optional[UserDefinedType] = None,
            tqdm=id_function,
    ):
        """
        add a data collection to this dataset.
        :param collection_name: name of the collection to add.
        :param data: list of json compatible objects .
        :param type_annotation: type annotation of the data.
        :param tqdm: Optional tqdm progress bar.
        :return:
        """
        for coll in self.meta.collections:
            if coll.name == collection_name:
                raise ValueError(f'collection {collection_name} already exists')

        new_coll = CollectionConfig(
            name=collection_name,
        )

        self.meta.collections.append(new_coll)

        target_fp = os.path.join(
            DatasetFileInternalPath.COLLECTION_FOLDER,
            collection_name,
            DatasetFileInternalPath.DATA_FILE
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            fn = os.path.join(temp_dir, 'temp-dataset.jsonl')
            with open(fn, 'w') as out:
                for item in tqdm(data):
                    out.write(json.dumps(item))
                    out.write("\n")
            self.zip_file.write(fn, arcname=target_fp)
        #
        # with self.zip_file.open(target_fp, 'w') as out:
        #     for item in tqdm(data):
        #         out.write(json.dumps(item).encode('utf-8'))
        #         out.write("\n".encode('utf-8'))

        if type_annotation is not None:
            type_file = os.path.join(
                DatasetFileInternalPath.COLLECTION_FOLDER,
                collection_name,
                DatasetFileInternalPath.TYPE_FILE
            )

            with self.zip_file.open(type_file, 'w') as out:
                out.write(
                    json.dumps(type_annotation.to_dict()).encode('utf-8')
                )

    def add_binary_file(self, fn: str, content: bytes):
        """
        Add a binary file to the dataset
        :param fn: name of the binary file.
        :param content: content in bytes.
        :return:
        """
        binary_file_path = DatasetFile.binary_file_path(fn)
        with self.zip_file.open(binary_file_path, 'w') as out:
            out.write(content)


class DatasetFileReader:
    def __init__(self, file_path):
        """
        Read a dataset, this object can be used as a context manager.

        This object must be closed.

        :param file_path:
        """
        self.zip_file = zipfile.ZipFile(file_path, 'r')

        with self.zip_file.open(DatasetFileInternalPath.META_FILE_NAME, 'r') as fd:
            self.meta = DatasetFileMeta(**json.load(fd))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.zip_file.close()

    def binary_files(self):
        """
        Open a binary file for read.
        :return: a file descriptor for the binary file to read.
        """
        prefix = DatasetFileInternalPath.BINARY_FOLDER + '/'
        for name in self.zip_file.namelist():
            if name.startswith(prefix):
                yield name[len(prefix):]

    def open_binary_file(self, filename):
        """
        Open a binary file for read.
        :param filename: name of the binary file.
        :return: a file descriptor for the binary file to read.
        """
        return self.zip_file.open(
            DatasetFile.binary_file_path(filename),
            'r'
        )

    def collection(self, collection_name):
        """
        Open a collection.
        :param collection_name: name of a collection
        :return: a CollectionReader object for the given collection name.
        """
        cfg = [c for c in self.meta.collections if c.name == collection_name]
        if len(cfg) == 0:
            raise ValueError(f"Collection {collection_name} do not exist")
        else:
            cfg = cfg[0]
        return CollectionReader(self.zip_file, collection_name, cfg)

    def coll(self, collection_name):
        return self.collection(collection_name)

    def collections(self):
        """
        List all collection names
        :return: list of collection names.
        """
        return [c.name for c in self.meta.collections]

    def __getitem__(self, item):
        return self.collection(item)


class CollectionReader(object):
    def __init__(self, zip_file, collection_name, config: CollectionConfig):
        """
        Collection Reader
        :param zip_file:
        :param collection_name:
        :param config:
        """
        self.zip_file = zip_file
        self.collection_name = collection_name
        self.config = config

    def type_annotation(self) -> Optional[ResolvedType]:
        ta_dict = self.type_annotation_dict()
        if ta_dict is not None:
            return parse_from_dict(ta_dict)
        return None

    def type_annotation_dict(self) -> Optional[dict]:
        entry = os.path.join(
            DatasetFileInternalPath.COLLECTION_FOLDER,
            self.collection_name,
            DatasetFileInternalPath.TYPE_FILE
        )
        if entry in self.zip_file.namelist():
            with self.zip_file.open(entry, 'r') as fd:
                return json.loads(fd.read().decode('utf-8'))
        return None

    def top(self, n=10):
        ret = []
        for i, row in enumerate(self):
            if i >= n:
                break
            ret.append(row)
        return ret

    def random_sample(self, n=10):
        return reservoir_sampling(self, n)

    def __iter__(self):
        """
        Iterate through the collection.
        :return:
        """
        entry = os.path.join(
            DatasetFileInternalPath.COLLECTION_FOLDER,
            self.collection_name,
            DatasetFileInternalPath.DATA_FILE
        )
        with self.zip_file.open(entry, 'r') as fd:
            for line in fd:
                line = line.strip()
                if len(line) > 0:
                    item = json.loads(line)
                    yield item

    def to_list(self):
        """
        Read the collection as list instead of iterator
        :return:
        """
        return list(self)


# Standard IO operations


def open_dataset_file(fp: str) -> 'DatasetFileReader':
    """
    Read a dataset file
    :param fp: path to the file
    :return:
    """
    return DatasetFileReader(fp)


def create(fp: str, compression=zipfile.ZIP_DEFLATED, compresslevel=9) -> 'DatasetFileWriter':
    """
    Create a dataset file to write
    :param fp: path to the file
    :param compression: compress mode for zip file.
    :param compresslevel: note that the default compression algorithm ZIP_LZMA do not use this value.
    :return:
    """
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return DatasetFileWriter(fp, compression=compression, compresslevel=compresslevel)
