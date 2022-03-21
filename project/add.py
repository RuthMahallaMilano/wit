import shutil
from pathlib import Path

from errors import WitError
from utils import get_repository_path, get_staging_area


def add_function(path_to_add: str) -> None:
    path = Path(path_to_add).resolve()
    repository = get_repository_path(path)
    if not repository:
        raise WitError("<.wit> file not found")
    copy_to_staging_area(path, repository)


def copy_to_staging_area(path: Path, repository: Path) -> None:
    staging_area_path = get_staging_area(repository)
    relative_path = path.relative_to(repository)
    if path.is_dir():
        copy_dir_to_staging_area(staging_area_path, path, relative_path)
    else:
        copy_file_to_staging_area(staging_area_path, path, relative_path)


def copy_file_to_staging_area(
    staging_area_path: Path, path: Path, relative_path: Path
) -> None:
    parents_path = relative_path.parents[0]
    destination = staging_area_path
    if parents_path.name:
        destination = staging_area_path / parents_path
        destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def copy_dir_to_staging_area(
    staging_area_path: Path, path: Path, relative_path: Path
) -> None:
    destination = staging_area_path / relative_path
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(path, destination)
