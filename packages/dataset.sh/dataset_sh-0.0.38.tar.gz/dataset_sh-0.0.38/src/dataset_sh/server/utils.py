def generate_download_code_py(hostname, dataset_name):
    template = f'''
import dataset_sh as dsh
dsh.remote(host="{hostname}").dataset("{dataset_name}").latest().download()
    '''.strip()
    return template


def generate_download_code_py_with_version(hostname, dataset_name, version):
    template = f'''
import dataset_sh as dsh
dsh.remote(host="{hostname}").dataset("{dataset_name}").version("{version}").download()
    '''.strip()
    return template


def generate_download_code_py_with_tag(hostname, dataset_name, tag):
    template = f'''
import dataset_sh as dsh
dsh.remote(host="{hostname}").dataset("{dataset_name}").tag("{tag}").download()
    '''.strip()
    return template


def generate_download_code_bash(hostname, dataset_name):
    template = f'''
dataset.sh remote -h {hostname} download {dataset_name}
    '''.strip()
    return template


def generate_download_code_bash_with_version(hostname, dataset_name, version):
    template = f'''
dataset.sh remote -h {hostname} download {dataset_name} -v {version}
    '''.strip()
    return template


def generate_download_code_bash_with_tag(hostname, dataset_name, tag):
    template = f'''
dataset.sh remote -h {hostname} download {dataset_name} -t {tag}
    '''.strip()
    return template


def generate_download_code(language, hostname, dataset_name, version=None, tag=None):
    if language == 'bash':
        if version:
            return generate_download_code_bash_with_version(hostname, dataset_name, version)
        elif tag and tag != 'latest':
            return generate_download_code_bash_with_tag(hostname, dataset_name, tag)
        else:
            return generate_download_code_bash(hostname, dataset_name)
    if language == 'python':
        if version:
            return generate_download_code_py_with_version(hostname, dataset_name, version)
        elif tag and tag != 'latest':
            return generate_download_code_py_with_tag(hostname, dataset_name, tag)
        else:
            return generate_download_code_py(hostname, dataset_name)
