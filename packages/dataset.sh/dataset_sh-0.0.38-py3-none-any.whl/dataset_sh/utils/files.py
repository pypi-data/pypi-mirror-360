import hashlib
import json
import os
from datetime import datetime

import requests


def checksum(file_path):
    md5_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(65536)
            if not data:
                break
            md5_hash.update(data)

    return md5_hash.hexdigest()


def filesize(file_path):
    file_size = os.path.getsize(file_path)
    return file_size


def file_creation_time(file_path):
    creation_time = os.path.getctime(file_path)
    # Convert it to a readable format
    readable_time = datetime.fromtimestamp(creation_time)
    return readable_time


def read_url_json(url, headers):  # pragma: no cover
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def download_url(url, target, headers):
    response = requests.get(url, headers=headers, stream=True, allow_redirects=True)

    has_tqdm = True
    try:
        from tqdm import tqdm
    except ModuleNotFoundError:  # pragma: no cover
        has_tqdm = False

    if response.status_code == 200:
        with open(target, "wb") as file:
            if has_tqdm:
                file_size = int(response.headers.get('content-length', 0))
                desc = "(Unknown total file size)" if file_size == 0 else ""
                with tqdm(
                        total=file_size, unit='iB', unit_scale=True
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
            else:
                for data in response.iter_content(chunk_size=1024):  # pragma: no cover
                    size = file.write(data)

        response.close()
    else:
        server_err = json.loads(response.content.decode('utf-8'))
        reason = server_err.get('reason', '')
        e = ValueError(f"Failed to download the file. Status code: {response.status_code}, reason: {reason}")
        response.close()
        raise e


def download_if_not_exists(url, filepath=None, **kwargs):
    """
    Download file to filepath if filepath not exists, additional arguments will be passed to `requests.get`.
    if filepath is None, the file will be downloaded to a file at current working dir with the
    last path element of the given url.

    Args:
        url:
        filepath:

    Returns:
        the downloaded file path.

    """
    if filepath is None:
        filename = url.split('/')[-1]
        if not filename:
            filename = '__download'
        filepath = os.path.join(os.getcwd(), filename)

    # Check if the file already exists
    if not os.path.exists(filepath):
        try:
            # The file does not exist; download it
            print(f"Downloading file from {url} to {filepath}")
            response = requests.get(url, **kwargs)
            response.raise_for_status()  # Raises HTTPError, if one occurred

            # Write the downloaded content to a file
            with open(filepath, 'wb') as file:
                file.write(response.content)
        except Exception as e:
            print(f"Failed to download or write file: {e}")
            # If the file was partially written, remove it to clean up
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Removed incomplete file: {filepath}")
            # Re-raise the exception to indicate failure
            raise
    else:
        print(f"File already exists: {filepath}")

    return filepath
