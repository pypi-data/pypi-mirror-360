import os

import requests
from tqdm import tqdm

from dataset_sh.utils.files import checksum


def direct_upload_to_url(presigned_url, file_path):
    with open(file_path, "rb") as f:
        response = requests.put(presigned_url, data=f)
        response.raise_for_status()


def multipart_upload_to_s3(
        instruction,
        file_path,
):
    """
    instruction:
    {
        'allowed': True,
        'action': 'upload',
        'parts': parts,
        'finished_parts': existing.finished,
        'cancel_url': cancel_url,
        'finish_url': finish_url
    }

    Args:
        instruction:
        file_path:
        silent:
        print_fn:

    Returns:

    """

    parts = instruction["parts"]
    finish_url = instruction["finish_url"]
    cancel_url = instruction["cancel_url"]

    uploaded = {p for p in instruction.get("finished_parts", [])}

    print(f'Starting multipart upload, in case you need to cancel, submit a post request to {cancel_url} ')

    with open(file_path, "rb") as f:
        total_parts = len(parts)
        for idx, part in enumerate(parts):

            idx_label = f"{idx + 1}/{total_parts}"

            """
            part = {
                    'part_id': part_number,
                    'start': chunk_start,
                    'size': chunk_end - chunk_start,
                    'url': create_part_upload_url(
                        hostname,
                        dataset_locator.namespace, dataset_locator.dataset_name,
                        checksum_value, file_size, part_number, token),
                    'report_url': create_part_progress_report_url(
                        hostname,
                        dataset_locator.namespace, dataset_locator.dataset_name,
                        checksum_value, file_size, part_number, token
                    )
            }
            """
            part_number = part["part_id"]
            start = int(part["start"])
            size = int(part["size"])
            upload_url = part["url"]
            report_url = part["report_url"]

            if part_number in uploaded:
                print(f"✅ {idx_label} - Skipping part id: {part_number}")
                continue

            f.seek(start)
            chunk = f.read(size)

            print(f"⬆️ {idx_label} Uploading part id {part_number} - Byte range: ({start}-{start + size})...")
            r = requests.put(upload_url, data=chunk)
            r.raise_for_status()

            # Mark part as uploaded
            resp = requests.post(report_url, json={
                "action": "progress-update",
                "part_id": part_number,
                "etag": r.headers.get("ETag"),
            })
            resp.raise_for_status()


    print("✅ Uploading done. Completing...")
    resp = requests.post(finish_url)
    resp.raise_for_status()
    print("🎉 Upload complete.")


class FileServerClient:
    endpoint: str
    headers: dict

    def __init__(self, endpoint: str, headers: dict = None):
        self.endpoint = endpoint
        self.headers = headers

    def upload(
            self,
            file: str,
            namespace: str,
            dataset_name: str,
            tags=None
    ):
        """

        Args:
            file:
            namespace:
            dataset_name:
            tags:

        Returns:

        """

        if not os.path.exists(file):
            raise FileNotFoundError(f"File not found: {file}")
        version = checksum(file)
        remote_filename = f'{namespace}/{dataset_name}:version={version}'
        instruction = self.request_upload(file, remote_filename, version, tags)
        if not instruction['allowed']:
            raise ValueError("Upload not allowed")

        multipart_upload_to_s3(
            instruction,
            file,
        )

        # if instruction['type'] == 'direct':
        #     # Direct upload to URL
        #     with open(file, 'rb') as f:
        #         response = requests.put(instruction['url'], data=f)
        #         response.raise_for_status()
        #     print("🎉 Upload complete.")
        #
        # elif instruction['type'] in ['multipart']:
        #     multipart_upload_to_s3(
        #         instruction,
        #         file,
        #     )
        # else:
        #     raise ValueError(f"Unsupported upload type: {instruction['type']}")

    def request_upload(self, file: str, remote_filename: str, checksum_value: str, tags=None):
        filesize = os.path.getsize(file)
        req = {
            'action': 'upload',
            'filename': remote_filename,
            'size': filesize,
            'checksum': checksum_value,
            'tags': tags,
        }

        resp = requests.post(self.endpoint, params=req, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def request_download(self, file: str):
        req = {
            'action': 'download',
            'file': file,
        }

        resp = requests.post(self.endpoint, params=req, headers=self.headers)
        resp.raise_for_status()
        return resp.json()
