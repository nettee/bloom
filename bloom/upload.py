import os
from pathlib import Path
from subprocess import run
from typing import List

from bloom import Article
from bloom.config import settings


def run_command(command: List[str]):
    print(' '.join(command))
    run(command)


def check_images(article: Article):
    print(f'Check images for article "{article.path}" ...')
    doc = article.read_doc()
    for image in doc.images():
        image_file = article.path_to(image.uri)
        if not image_file.exists():
            print(f'Warning: image `{image.uri}` does not exist')


def upload_image_files(article: Article, files: List[Path]):
    name = article.meta.base.name
    user = settings.image.user
    host = settings.image.host
    target_dir = os.path.join(settings.image.baseDir, name)

    mkdir_command = ['ssh', f'{user}@{host}', 'mkdir', '-p', target_dir]
    scp_command = ['scp', '-r'] + [str(file) for file in files] + [f'{user}@{host}:{target_dir}']

    run_command(mkdir_command)
    run_command(scp_command)


def upload_images(article: Article):
    name = article.meta.base.name
    print(f'Uploading images for {name}...')

    doc = article.read_doc()
    image_files = [article.path_to(image.uri) for image in doc.images()]
    upload_image_files(article, image_files)


def upload(article: Article):
    check_images(article)
    upload_images(article)
