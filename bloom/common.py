

def _pretty_print_dict(d: dict, prefix: str = ''):
    for k, v in d.items():
        key = k if prefix == '' else f'{prefix}.{k}'
        if isinstance(v, dict):
            _pretty_print_dict(v, key)
        else:
            print(f'{key}={v}')


def print_config(d: dict):
    _pretty_print_dict(d)
