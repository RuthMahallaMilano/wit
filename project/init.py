from pathlib import Path

from project.errors import WitExistsError
from project.utils import (
    get_activated_path,
    get_images_path,
    get_staging_area_path,
    get_wit_path,
)


def init_function() -> None:
    cwd = Path.cwd()
    wit_path = get_wit_path(cwd)
    if wit_path.exists():
        raise WitExistsError("The folder is already a wit directory.")
    wit_path.mkdir()
    images_path = get_images_path(cwd)
    images_path.mkdir()
    staging_area_path = get_staging_area_path(cwd)
    staging_area_path.mkdir()
    activated_path = get_activated_path(cwd)
    activated_path.write_text("master")
