from project.utils import get_all_files_in_repository_and_subs


def test_get_all_files_in_repository(test_folder, empty_folder):
    all_files = get_all_files_in_repository_and_subs(test_folder)
    assert empty_folder.relative_to(test_folder) in set(all_files)
