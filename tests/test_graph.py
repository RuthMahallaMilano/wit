import os
from pathlib import Path

import pytest

from project.add import add_function
from project.branch import branch_function
from project.checkout import checkout_function
from project.commit import commit_function
from project.errors import WitError
from project.graph import graph_function
from project.merge import merge_function
from project.utils import (
    get_branches_commits,
    get_head_reference,
    get_references_path,
    get_wit_dir,
)


def test_raise_error(tmp_path, test_folder):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        graph_function()


def test_graph_function(test_folder):
    os.chdir(test_folder)
    create_branch_and_checkout("branch1")
    change_add_and_commit_file3(test_folder)
    checkout_function("master")
    merge_function("branch1")
    dot_source = graph_function(test=True)
    current_commit_id = get_head_reference(test_folder)
    wit_dir = get_wit_dir(test_folder)
    references_file = get_references_path(test_folder)
    assert wit_dir / f"Graph_{current_commit_id}.pdf" in set(wit_dir.iterdir())
    for commit in get_branches_commits(references_file).values():
        assert commit in dot_source


def create_branch_and_checkout(branch_name: str) -> None:
    branch_function(branch_name)
    checkout_function(branch_name)


def change_add_and_commit_file3(test_folder: Path) -> None:
    file3 = test_folder / r"folder1\folder2\file3.txt"
    file3.write_text("1")
    add_function(str(file3))
    commit_function("add file3")
