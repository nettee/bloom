from pathlib import Path

from base import config


def list_all():
    root = Path(config.bloomstore)
    for item in root.iterdir():
        print(item)
