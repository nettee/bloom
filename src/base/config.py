import os
from pathlib import Path

bloomstore = '/Users/william/bloomstore'


def get_bloomstore(env_name: str = 'BLOOMSTORE') -> Path:
    store = os.getenv(env_name)
    if store is None:
        raise RuntimeError('Environment variable BLOOMSTORE not set')
    path = Path(store)
    if not path.exists():
        raise RuntimeError(f'BLOOMSTORE ({path}) directory not exists')
    return path
