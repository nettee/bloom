import os
from pathlib import Path
from subprocess import run
from typing import List

from bloom import Article
from bloom.config import settings


def run_command(command: List[str]):
    print(' '.join(command))
    run(command)


def upload_image_files(article: Article, files: List[Path]):
    name = article.meta.base.name
    user = settings.image.user
    host = settings.image.host
    target_dir = os.path.join(settings.image.baseDir, name)

    mkdir_command = ['ssh', f'{user}@{host}', 'mkdir', '-p', target_dir]
    scp_command = ['scp', '-r'] + [str(file) for file in files] + [f'{user}@{host}:{target_dir}']

    run_command(mkdir_command)
    run_command(scp_command)


def upload(article: Article, all=False):
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

    upload_image_files(article, image_files)
