def generate_bash_import(site_url, dataset_full_name):
    url = generate_download_url(site_url, dataset_full_name)
    code = f"""
import dataset_sh
dataset_sh.import_url("{dataset_full_name}", "{url}")   
    """.strip()
    return code


def generate_python_import(site_url, dataset_full_name):
    url = generate_download_url(site_url, dataset_full_name)
    code = f"""
dataset.sh import {dataset_full_name} -u {url}
    """.strip()
    return code


def generate_download_url(site_url, dataset_full_name):
    return f"{site_url}/api/dataset/{dataset_full_name}/file"
