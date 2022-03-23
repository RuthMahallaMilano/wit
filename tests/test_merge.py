import os

import pytest

from project.errors import WitError
from project.merge import merge_function


def test_raise_error(tmp_path):
    os.chdir(tmp_path)
    test_file = tmp_path / "test.txt"
    test_file.write_text("")
    with pytest.raises(WitError):
        merge_function("")


# on master.
# new branch > change file > checkout master > merge new branch
# assert file has changed

# on master.
# new branch > change file > checkout master > change file > merge new branch
# assert: raise NotImplementedError - f"{file_path} was changed in both branches. Not implemented yet."
