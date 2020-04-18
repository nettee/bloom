import os
from pathlib import Path


def get_project_path() -> Path:
    script_path = os.path.realpath(__file__)
    project_path = Path(script_path).parent.parent
    return project_path
