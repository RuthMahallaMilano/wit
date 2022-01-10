import os
from pathlib import Path


def init() -> None:
    cwd = os.getcwd()
    wit_path = os.path.join(cwd, '.wit')
    os.mkdir(wit_path)
    os.mkdir(os.path.join(wit_path, 'images'))
    os.mkdir(os.path.join(wit_path, 'staging_area'))
    activated_path = os.path.join(wit_path, 'activated.txt')
    Path(activated_path).write_text('master')
