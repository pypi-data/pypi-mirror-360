import os.path
import click

from dataset_sh.multipart.upload import MultipartUploadClient

file_size = 10 * 1024 * 1024  # 100MB


@click.command()
@click.option('--fn', default='test')
def run(fn):
    tmp_file = '/tmp/largefile'
    if not os.path.exists(tmp_file):
        with open(tmp_file, 'wb') as file:
            file.write(os.urandom(file_size))

    client = MultipartUploadClient(f'http://127.0.0.1:9900/upload/{fn}', tmp_file)
    client.upload()


if __name__ == '__main__':
    run()
