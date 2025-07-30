import json
import math
import os.path
import secrets
import shutil
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from dataset_sh.utils.files import checksum as calculate_checksum


def merge_binary_files(file_list, output_file):
    """
    Merges multiple binary files into a single file.

    :param file_list: List of paths to the binary files to be merged.
    :param output_file: Path to the output file where the merged content will be written.
    """
    with open(output_file, 'wb') as outfile:
        for file_name in file_list:
            with open(file_name, 'rb') as infile:
                outfile.write(infile.read())


def read_file_range(filepath, offset, length):
    with open(filepath, 'rb') as file:
        file.seek(offset)
        file_data = file.read(length)
        return file_data


class FilePartsInfo(BaseModel):
    checksum: str
    parts_count: int
    total_length: int
    chunk_size: int
    secret: str = Field(default_factory=lambda: secrets.token_hex(8))
    expireAt: datetime = Field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    finished: list[int] = Field(default_factory=list)

    # def chunk_size(self, part_id: int) -> int:
    #     if part_id < 0 or part_id >= self.parts_count:
    #         raise ValueError("part_id must be within the range of the total number of parts")
    #
    #     standard_chunk_size = self.total_length // self.parts_count
    #     remainder = self.total_length % self.parts_count
    #
    #     # If it's the last part and there's a remainder, add it to the last chunk's size
    #     if part_id == self.parts_count - 1 and remainder:
    #         return standard_chunk_size + remainder
    #     else:
    #         return standard_chunk_size


class MultipartFileWriter(object):
    """
    A multipart file creator,
    """

    def __init__(self, target, checksum, file_length, chunk_size=1 * 1000 * 1000):
        """

        Args:
            target: the final location of the file
            file_length: length of the file.
        """
        self.target = target
        self.checksum = checksum
        self.file_length = file_length
        self.chunk_size = chunk_size

    @property
    def parts_folder(self):
        return f"{self.target}__parts_folder"

    @property
    def progress_file(self):
        return f"{self.target}._progress"

    def start(self):
        """
        when it starts, it will create a [target]._progress file, and write done the FilePartsInfo object in that file.
        It will also create a [target]._parts folder
        """
        if not os.path.exists(self.parts_folder):
            os.makedirs(self.parts_folder)
        parts_count = int(math.ceil(self.file_length / self.chunk_size))
        info = FilePartsInfo(
            checksum=self.checksum,
            parts_count=parts_count,
            total_length=self.file_length,
            chunk_size=self.chunk_size
        )
        with open(self.progress_file, 'w') as f:
            json.dump(info.model_dump(mode='json'), f)

    def part_files(self) -> list[str]:
        """
        Returns: list of file path of all
        """
        return [os.path.join(self.parts_folder, f"{i}") for i in range(self.load_existing_progress().parts_count)]

    def part_file(self, part_id: int) -> str:
        """
        Returns: path of part part_id, i.e. [target]
        """
        return os.path.join(self.parts_folder, f"{part_id}")

    def complete_marker(self, part_id: int) -> str:
        """
        Returns: path of complete_marker for part part_id
        """
        return os.path.join(self.parts_folder, f"{part_id}.done")

    def load_existing_progress(self) -> Optional[FilePartsInfo]:
        """
        Load the [target]._progress file if exists and return the parsed FilePartsInfo object.
        If the file do not exist yet, return None
        Returns: FilePartsInfo object
        """
        if not os.path.exists(self.progress_file):
            return None
        with open(self.progress_file, 'r') as f:
            data = json.load(f)
        info = FilePartsInfo(**data)
        info.finished = []
        for part_id in range(info.parts_count):
            if os.path.exists(self.complete_marker(part_id)):
                info.finished.append(part_id)

        return info

    def get_completed_parts(self) -> list[int]:
        """
        Returns: list of parts completed, i.e. complete marker exists.
        """
        info = self.load_existing_progress()
        if not info:
            return []
        completed = []
        for part_id in range(info.parts_count):
            if os.path.exists(self.complete_marker(part_id)):
                completed.append(part_id)
        return completed

    def get_uncompleted_parts(self) -> list[int]:
        """
        Returns: list of parts that is missing, i.e. complete marker does not exist.
        """
        info = self.load_existing_progress()
        if not info:
            return []
        uncompleted = []
        for part_id in range(info.parts_count):
            if not os.path.exists(self.complete_marker(part_id)):
                uncompleted.append(part_id)
        return uncompleted

    def mark_file_as_complete(self, part_id: int):
        """
        Returns: create complete marker.
        """
        marker_path = self.complete_marker(part_id)
        with open(marker_path, 'w') as f:
            f.write('')

    def terminate(self):
        '''
        Remove  [target]._progress and all created file parts and markers.
        Returns:

        '''
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        if os.path.exists(self.parts_folder):
            shutil.rmtree(self.parts_folder)

    def done(self):
        """
        Merge all parts file in _parts folder and if the checksum of the final file match the provided value.
        Returns:

        """
        info = self.load_existing_progress()
        if not info:
            raise Exception("No progress info found.")
        merge_binary_files(self.part_files(), self.target)

        if self.checksum == calculate_checksum(self.target):
            self.terminate()
        else:
            raise ValueError('checksum failed.')


class UploadServerResponse(BaseModel):
    action: str
    info: FilePartsInfo


class DownloadServerResponse(BaseModel):
    action: str
    info: FilePartsInfo
