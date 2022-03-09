from pathlib import Path
import pytest

from project import init


def test_init(test_folder):
    init.init_function(test_folder)
    test_wit_path = Path(test_folder).joinpath('.wit')
    assert test_wit_path.is_dir()
    assert test_wit_path.joinpath('images').is_dir()
    assert test_wit_path.joinpath('staging_area').is_dir()
    assert test_wit_path.joinpath('activated.txt').read_text() == 'master'
