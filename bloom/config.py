import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dacite import from_dict

from bloom.common import print_config

SETTING_FILES = ('settings.yml', 'settings.yaml', 'settings.toml')
bloomstore = '/Users/william/bloomstore'


@dataclass
class HostImageSetting:
    host: Optional[str] = field(default=None)
    user: Optional[str] = field(default=None)
    baseDir: Optional[str] = field(default='.')
    baseUrlPath: Optional[str] = field(default=None)


@dataclass
class OssImageSetting:
    region: Optional[str] = field(default=None)
    bucket: Optional[str] = field(default=None)
    endpoint: Optional[str] = field(default=None)
    baseDir: Optional[str] = field(default='.')
    accessKeyId: Optional[str] = field(default=None)
    accessKeySecret: Optional[str] = field(default=None)
    publicHost: Optional[str] = field(default=None)


@dataclass
class ImageSetting:
    default: str
    host: Optional[HostImageSetting] = field(default=None)
    oss: Optional[OssImageSetting] = field(default=None)


@dataclass
class Setting:
    bloomstore: str
    image: ImageSetting


settings: Optional[Setting] = None


def find_settings_file() -> Path:
    settings_dir = Path.home() / '.bloom'
    for filename in SETTING_FILES:
        settings_file = settings_dir / filename
        if settings_file.exists():
            print(f'Load bloom settings from {settings_file}')
            return settings_file
    print('Bloom settings not found. Quit.')
    exit(1)


def load_settings():
    settings_file = find_settings_file()
    with settings_file.open('r') as f:
        data = yaml.load(f, Loader=yaml.CLoader)
        global settings
        settings = from_dict(data_class=Setting, data=data)


# Load settings on import
load_settings()


def list_settings():
    d = dataclasses.asdict(settings)
    print_config(d)


def get_bloomstore() -> Path:
    path = Path(settings.bloomstore)
    if not path.exists():
        raise RuntimeError(f'BLOOMSTORE ({path}) directory not exists')
    return path


if __name__ == '__main__':
    list_settings()
