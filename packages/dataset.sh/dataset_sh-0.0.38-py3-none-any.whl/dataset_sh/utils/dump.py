from typing import Optional

from easytype.core import UserDefinedType

from dataset_sh import create
from dataset_sh.utils.author import load_author_profile
from dataset_sh.utils.files import checksum
from dataset_sh.utils.misc import get_tqdm
from dataset_sh.constants import DEFAULT_COLLECTION_NAME


def dump_single_collection(
        fn,
        data,
        name=DEFAULT_COLLECTION_NAME,
        type_annotation: Optional[UserDefinedType] = None,
        description: Optional[str] = None,
        silent=False,
        load_author=True,
):
    """
    Args:
        fn: output file path.
        data: data of the collection.
        name: name of the collection, default to `dataset_sh.constants.DEFAULT_COLLECTION_NAME`
        type_annotation: type annotation for the collection.
        description: describe this version.
        silent: do not report progress if set to True.
    Returns:
    """
    with create(fn) as out:

        if load_author:
            author_info = load_author_profile()
            if author_info:
                author = author_info.get("author", None)
                author_email = author_info.get("author_email", None)

                if author:
                    out.meta.author = author
                if author_email:
                    out.meta.authorEmail = author_email

        if description:
            out.meta.description = description
        out.add_collection(name, data, type_annotation=type_annotation, tqdm=get_tqdm(silent=silent))
    return checksum(fn)


def dump_collections(
        fn,
        data_dict,
        type_dict=None,
        description: Optional[str] = None,
        report_item_progress=False,
        report_collection_progress=False,
        load_author=True,
):
    """
    Args:
        fn: output file path.
        data_dict: data for each collection, dict key is collection name, value is collection data.
        type_dict: type annotation for each collection, dict key is collection name, value is type annotation.
        description: describe this version.
        report_item_progress:
        report_collection_progress:

    Returns:

    """
    if type_dict is None:
        type_dict = {}
    inner_tqdm = get_tqdm(silent=not report_item_progress)
    with create(fn) as out:
        if description:
            out.meta.description = description

        if load_author:
            author_info = load_author_profile()
            if author_info:
                author = author_info.get("author", None)
                author_email = author_info.get("author_email", None)

                if author:
                    out.meta.author = author
                if author_email:
                    out.meta.authorEmail = author_email

        for name, data in data_dict.items():
            if report_collection_progress:
                print(f'Importing collection {name}')
            if len(data) > 0:
                type_annotation = type_dict.get(name, None)
                out.add_collection(name, data, type_annotation=type_annotation, tqdm=inner_tqdm)
    return checksum(fn)
