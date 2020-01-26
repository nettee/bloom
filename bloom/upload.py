import os
from subprocess import run
from typing import List

from bloom import Article
from bloom.config import settings


def run_command(command: List[str]):
    print(' '.join(command))
    run(command)


def upload_images(article: Article):
    name = article.meta.base.name
    print(f'Uploading images for {name}...')

    image_path = article.image_path()

    user = settings.image.user
    host = settings.image.host
    target_dir = os.path.join(settings.image.baseDir, name)

    mkdir_command = ['ssh', f'{user}@{host}', 'mkdir', '-p', target_dir]
    scp_command = ['scp', '-r'] + [str(item) for item in image_path.iterdir()] + [f'{user}@{host}:{target_dir}']

    run_command(mkdir_command)
    run_command(scp_command)


def upload(article: Article):
    upload_images(article)
