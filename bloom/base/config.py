import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import toml
from dacite import from_dict

bloomstore = '/Users/william/bloomstore'


@dataclass
class ImageSetting:
    host: Optional[str] = field(default=None)
    user: Optional[str] = field(default=None)
    base_dir: Optional[str] = field(default='.')
    base_url_path: Optional[str] = field(default=None)


@dataclass
class Setting:
    bloomstore: str
    image: ImageSetting


SETTINGS_FILE: Path = Path.home() / '.bloom' / 'settings.toml'
settings: Optional[Setting] = None


def load_settings():
    print(f'Load bloom settings from {SETTINGS_FILE}')
    with SETTINGS_FILE.open('r') as f:
        data = toml.load(f)
        global settings
        settings = from_dict(data_class=Setting, data=data)


# Load settings on import
if SETTINGS_FILE.exists():
    load_settings()


def get_bloomstore() -> Path:
    path = Path(settings.bloomstore)
    if not path.exists():
        raise RuntimeError(f'BLOOMSTORE ({path}) directory not exists')
    return path


if __name__ == '__main__':
    load_settings()