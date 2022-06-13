import os

import pytest

from project.branch import branch_function
from project.checkout import checkout_function
from project.errors import WitError
from project.graph import graph_function
from project.merge import get_parents_commits, merge_function
from project.utils import (
    get_commit_id_of_branch,
    get_head_reference,
    get_references_path,
    get_wit_path,
)
from tests.conftest import change_add_and_commit_file


def test_raise_wit_error(tmp_path, test_folder):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        graph_function()


def test_graph_function(test_folder, file1, file3):
    os.chdir(test_folder)
    change_add_and_commit_file(file1, "")
    branch_function("branch1")
    checkout_function("branch1")
    change_add_and_commit_file(file3, "1")
    checkout_function("master")
    merge_function("branch1")
    references_file = get_references_path(test_folder)
    branch_commit_id = get_commit_id_of_branch(test_folder, "branch1", references_file)
    dot_source = graph_function()
    current_commit_id = get_head_reference(test_folder)
    wit_dir = get_wit_path(test_folder)
    commits_in_graph = get_commits_in_graph(
        branch_commit_id, current_commit_id, test_folder
    )
    assert wit_dir / f"Graph_{current_commit_id}.pdf" in set(wit_dir.iterdir())
    for commit in commits_in_graph:
        assert commit in dot_source


def get_commits_in_graph(branch_commit_id, current_commit_id, test_folder):
    parents_commits_of_branch = set(get_parents_commits(test_folder, branch_commit_id))
    parents_commits_of_master = set(get_parents_commits(test_folder, current_commit_id))
    commits_in_graph = parents_commits_of_branch.union(parents_commits_of_master)
    return commits_in_graph
