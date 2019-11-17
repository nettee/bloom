import re
from pathlib import Path

from base import config


def formalize_title(title):
    words = re.split(r'[^A-Za-z0-9]', title)
    return '-'.join(w.lower() for w in words if w != '')


def create_post(title):
    name = formalize_title(title)

    root = Path(config.bloomstore)
    post_dir = root / name
    assert not post_dir.exists()
    post_dir.mkdir()

    post = post_dir / f'{name}.md'
    with post.open('w') as f:
        print(f'# {title}', file=f)

    post_img_dir = post_dir / 'img'
    post_img_dir.mkdir()
