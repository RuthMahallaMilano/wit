import os

import pytest

from project.add import add_function
from project.branch import branch_function
from project.checkout import checkout_function
from project.commit import commit_function
from project.errors import WitError
from project.graph import graph_function
from project.merge import merge_function, get_parents_commits
from project.utils import (
    get_head_reference,
    get_references_path,
    get_wit_dir, get_commit_id_of_branch,
)


def test_raise_wit_error(tmp_path, test_folder):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        graph_function()


def test_graph_function(test_folder):
    os.chdir(test_folder)
    create_branch_and_checkout("branch1")
    change_add_and_commit_file3(test_folder)
    references_file = get_references_path(test_folder)
    checkout_function("master")
    branch_commit_id = get_commit_id_of_branch(test_folder, "branch1", references_file)
    merge_function("branch1")
    dot_source = graph_function(test=True)
    current_commit_id = get_head_reference(test_folder)
    wit_dir = get_wit_dir(test_folder)
    commits_in_graph = get_commits_in_graph(branch_commit_id, current_commit_id, test_folder)
    assert wit_dir / f"Graph_{current_commit_id}.pdf" in set(wit_dir.iterdir())
    for commit in commits_in_graph:
        assert commit in dot_source


def get_commits_in_graph(branch_commit_id, current_commit_id, test_folder):
    parents_commits_of_branch = set(get_parents_commits(test_folder, branch_commit_id))
    parents_commits_of_master = set(get_parents_commits(test_folder, current_commit_id))
    commits_in_graph = parents_commits_of_branch.union(parents_commits_of_master)
    return commits_in_graph


def create_branch_and_checkout(branch_name):
    branch_function(branch_name)
    checkout_function(branch_name)


def change_add_and_commit_file3(test_folder):
    file3 = test_folder / r"folder1\folder2\file3.txt"
    file3.write_text("1")
    add_function(file3)
    commit_function("add file3")
