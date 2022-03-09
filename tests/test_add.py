import os
from pathlib import Path
import pytest
from project import add, init


# @pytest.mark.parametrize(
#     'file_path, parent',
#     [
#         (Path(''))
#     ]
# )



@pytest.mark.parametrize(
    'path, parent',
    [
        (Path('test_wit').joinpath('file1.txt'), Path('test_wit')),
        (Path('test_wit').joinpath('folder1', 'folder2'), Path('test_wit')),
        (Path('test_wit').joinpath('folder1', 'folder2', 'file3'), Path('test_wit'))
    ]
)
def test_get_directory_with_wit(test_folder, path, parent):
    init.init_function(test_folder)
    assert add.get_repository_path(path) == parent


@pytest.mark.parametrize(
    'destination_in_wit, file, new_destination',
    [
        (Path('file1.txt'), Path('test_wit').joinpath('file1.txt'), Path('test_wit')),
        (Path('folder1').joinpath('folder2'), Path('test_wit')),
        (Path('test_wit').joinpath('folder1', 'folder2', 'file3'), Path('test_wit'))
    ]
)
def test_save_the_copy(test_folder, destination_in_wit, file, new_destination):
    init.init_function(test_folder)
    destination = Path('test_wit').joinpath('.wit', 'staging_area')
    add.save_the_copy(destination.joinpath(destination_in_wit), file)
    assert destination.joinpath(destination_in_wit).exists()

# def test_add():
#     pass