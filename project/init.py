import os
from pathlib import Path

from errors import WitExistsError


def init_function() -> None:
    cwd = os.getcwd()
    wit_path = os.path.join(cwd, ".wit")
    if os.path.exists(wit_path):
        raise WitExistsError("The folder already has .wit directory")
    os.mkdir(wit_path)
    os.mkdir(os.path.join(wit_path, "images"))
    os.mkdir(os.path.join(wit_path, "staging_area"))
    activated_path = os.path.join(wit_path, "activated.txt")
    Path(activated_path).write_text("master")
