import math
from urllib.parse import urlencode

from dataset_sh.clients.locator import DatasetLocator
from dataset_sh.clients.remote import url_join


def create_download_url(hostname, locator, token):
    query_string = urlencode({
        "token": token
    })

    if locator.version is not None:
        p = f'api/dataset/{locator.namespace}/{locator.dataset_name}/version/{locator.version}/file?{query_string}'
    elif locator.tag is not None:
        p = f'api/dataset/{locator.namespace}/{locator.dataset_name}/tag/{locator.tag}/file?{query_string}'
    else:
        p = f'api/dataset/{locator.namespace}/{locator.dataset_name}/tag/latest/file?{query_string}'

    return url_join(hostname, p)


def get_chunk_size(
        file_size,
        min_chunk_size=5 * 1024 * 1024,
        max_chunks=10_000
):
    chunk_size = max(min_chunk_size, (file_size + max_chunks - 1) // max_chunks)
    chunk_count = int(math.ceil(file_size / chunk_size))
    return chunk_size, chunk_count


def suggest_parts(
        hostname,
        dataset_locator: DatasetLocator,
        file_size,
        checksum_value,
        token,
        min_chunk_size=5 * 1024 * 1024,
        max_chunks=10_000
):
    """
    calculate multipart upload parts based on the given parameters.
    :param file_size: size of the file in bytes
    :param min_chunk_size: minimal chunk size in bytes
    :param max_chunks: maximal number of chunks
    :return: list of part dicts {start: int, end: int, part: int}, the end is not inclusive
    """
    file_size = int(file_size)
    if file_size <= 0:
        return []

    chunk_size, chunk_count = get_chunk_size(file_size, min_chunk_size, max_chunks)

    parts = []

    for i in range(chunk_count):
        chunk_start = i * chunk_size
        chunk_end = min(chunk_start + chunk_size, file_size)
        part_number = i
        parts.append({
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
        })

    return parts


def create_part_upload_url(hostname, namespace, dataset_name, checksum_value, file_size, part_number: int, token: str):
    query_string = urlencode({
        "token": token,
        "part_id": part_number,
        'checksum_value': checksum_value,
        'file_size': file_size,
    })

    p = f'api/dataset/{namespace}/{dataset_name}/upload?{query_string}'
    return url_join(hostname, p)


def create_part_progress_report_url(hostname, namespace, dataset_name, checksum_value, file_size, part_number: int,
                                    token: str):
    query_string = urlencode({
        "token": token,
        'action': 'progress-update',
        "part_id": part_number,
        'checksum_value': checksum_value,
        'file_size': file_size,
    })

    p = f'api/dataset/{namespace}/{dataset_name}/upload-progress?{query_string}'
    return url_join(hostname, p)


def create_part_finish_url(hostname, namespace, dataset_name, checksum_value, file_size, part_number: int, token: str):
    query_string = urlencode({
        "token": token,
        'action': 'done',
        "part_id": part_number,
        'checksum_value': checksum_value,
        'file_size': file_size,
    })

    p = f'api/dataset/{namespace}/{dataset_name}/upload-progress?{query_string}'
    return url_join(hostname, p)


def create_upload_finish_url(hostname, namespace, dataset_name, checksum_value, file_size, tags, token: str):
    query_string = urlencode({
        "token": token,
        'action': 'done',
        "tags": tags,
        'checksum_value': checksum_value,
        'file_size': file_size,
    })

    p = f'api/dataset/{namespace}/{dataset_name}/upload-progress?{query_string}'
    return url_join(hostname, p)


def create_upload_cancel_url(hostname, namespace, dataset_name, checksum_value, file_size, token: str):
    query_string = urlencode({
        "token": token,
        'action': 'abort',
        'checksum_value': checksum_value,
        'file_size': file_size,
    })

    p = f'api/dataset/{namespace}/{dataset_name}/upload-progress?{query_string}'
    return url_join(hostname, p)
