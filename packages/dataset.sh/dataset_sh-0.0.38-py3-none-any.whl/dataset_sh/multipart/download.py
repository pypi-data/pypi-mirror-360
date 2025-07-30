import json
from dataclasses import dataclass

import requests
from dataset_sh.multipart.multipart import MultipartFileWriter


@dataclass
class DirectDownloadInstruction:
    direct_download_url: str
    type: str = 'direct'


@dataclass
class MultipartDownloadInstruction:
    file_length: int
    checksum: str
    multipart_download_url: str
    type: str = 'multipart'


class MultipartDownloadClient(object):

    def __init__(self, source_url, target):
        self.target = target
        self.source_url = source_url

    def _get_instruction(self):
        resp = requests.get(self.source_url, params={'action': 'request-info'})
        resp.raise_for_status()
        resp_json = json.loads(resp.content.decode('utf-8'))
        download_type = resp_json.get('type', None)
        if download_type == 'direct':
            return DirectDownloadInstruction(direct_download_url=resp_json['direct_download_url'])
        elif download_type == 'multipart':
            return MultipartDownloadInstruction(
                file_length=resp_json['file_length'],
                checksum=resp_json['checksum'],
                multipart_download_url=resp_json['multipart_download_url']
            )
        else:
            raise ValueError(f'Unknown instruction type: {download_type}')

    def download(self):
        instruction = self._get_instruction()
        if instruction.type == 'direct':
            resp = requests.get(instruction.direct_download_url)
            resp.raise_for_status()
            with open(self.target, 'wb') as fd:
                fd.write(resp.content)

        else:
            writer = MultipartFileWriter(
                self.target,
                file_length=instruction.file_length,
                checksum=instruction.checksum,
            )
            writer.start()
            todo = writer.get_uncompleted_parts()
            for part_id in todo:
                part_file = writer.part_file(part_id)

                resp = requests.get(instruction.multipart_download_url, params={'part_id': part_id})
                resp.raise_for_status()
                with open(part_file, 'wb') as fd:
                    fd.write(resp.content)

                writer.mark_file_as_complete(part_id)
            writer.done()
