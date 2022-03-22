import os
import shutil
from pathlib import Path
import pytest

from project.errors import WitExistsError
from project.init import init_function
from project.utils import get_wit_dir, get_images_path, get_staging_area, get_activated_path


def test_wit_dir(test_folder):
    wit_path = get_wit_dir(test_folder)
    assert wit_path.is_dir()
    assert get_images_path(test_folder).is_dir()
    assert get_staging_area(test_folder).is_dir()
    assert get_activated_path(test_folder).read_text() == "master"


def test_wit_exists(test_folder):
    os.chdir(test_folder)
    with pytest.raises(WitExistsError):
        init_function()

