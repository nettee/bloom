import os
from pathlib import Path
from subprocess import run
from typing import List

from bloom import Article
from bloom.config import settings


def run_command(command: List[str]):
    print(' '.join(command))
    run(command)


class Uploader:

    def upload(self, article: Article, files: List[Path]):
        pass


class NowhereUploader(Uploader):

    def upload(self, article: Article, files: List[Path]):
        print('Upload to nowhere! Please pass the --to parameter')


class HostUploader(Uploader):

    def upload(self, article: Article, files: List[Path]):
        print(f'Uploading {len(files)} files to host...')
        name = article.meta.base.name
        user = settings.image.user
        host = settings.image.host
        target_dir = os.path.join(settings.image.baseDir, name)

        print('name =', name)
        print('user =', user)
        print('host =', host)
        print('target_dir =', target_dir)

        mkdir_command = ['ssh', f'{user}@{host}', 'mkdir', '-p', target_dir]
        scp_command = ['scp', '-r'] + [str(file) for file in files] + [f'{user}@{host}:{target_dir}']

        run_command(mkdir_command)
        run_command(scp_command)


class OssUploader(Uploader):

    def upload(self, article: Article, files: List[Path]):
        print(f'Uploading {len(files)} files to oss...')


def get_uploader(to):
    uploader_class = {
        'host': HostUploader,
        'oss': OssUploader,
    }.get(to, NowhereUploader)
    return uploader_class()


def upload(article: Article, to='nowhere', all=False):
    name = article.meta.base.name
    print(f'Uploading images for {name}...')

    if all:
        image_files = [file for file in article.image_path().iterdir() if not file.stem.startswith('.')]
    else:
        doc = article.read_doc()
        image_files = [article.path_to(image.uri) for image in doc.images()]
        for image_file in image_files:
            if not image_file.exists():
                print(f'Warning: image `{str(image_file)}` does not exist')

    get_uploader(to).upload(article, image_files)
