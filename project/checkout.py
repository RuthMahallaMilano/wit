import os
from pathlib import Path
import shutil

from add import get_repository_path
from commit import get_parent_head, get_commit_id_of_branch
from errors import FilesDoesntMatchError, WitError, BranchDoesntExistError
from status import get_changes_to_be_committed, get_changes_not_staged_for_commit, get_all_files_in_directory_and_subs


def checkout(commit_id_or_branch: str) -> None:
    repository = get_repository_path(Path.cwd())
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    last_commit_id = get_parent_head(repository)
    last_commit_path = os.path.join(repository, '.wit', 'images', last_commit_id)
    if not repository:
        raise WitError("<.wit> file not found")
    if (
        list(get_changes_to_be_committed(last_commit_path, staging_area_path))
        or list(get_changes_not_staged_for_commit(repository, staging_area_path))
    ):
        raise FilesDoesntMatchError("There are files added or changed after last commit")
    references_file = repository.joinpath('.wit', 'references.txt')
    commit_id = get_commit_id_of_branch(commit_id_or_branch, references_file)
    if not commit_id:
        raise BranchDoesntExistError("Branch doesn't exist.")
    if commit_id != commit_id_or_branch:
        write_activated(commit_id_or_branch, repository)
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    change_files_in_main_folder(commit_path, repository)
    change_head_in_references_file(commit_id, references_file)
    change_staging_area_folder(staging_area_path, commit_path)
    if commit_id != commit_id_or_branch:
        write_activated(commit_id_or_branch, repository)


def write_activated(commit_id_or_branch: str, repository: Path) -> None:
    activated_path = repository.joinpath('.wit', 'activated.txt')
    activated_path.write_text(commit_id_or_branch)


def change_head_in_references_file(commit_id: str, references_file: Path) -> None:
    with references_file.open() as file:
        branches = file.readlines()[1:]
        branches_txt = ''.join(branches)
    references_file.write_text(f'HEAD={commit_id}\n{branches_txt}')


# def get_commit_id_of_branch(commit_id_or_branch: str, references_file: Path) -> str:
#     branch_regex = re.compile(r"^(?P<branch_name>\w+)=(?P<branch_id>\w{20})$")
#     with references_file.open() as file:
#         for line in file:
#             match = branch_regex.match(line)
#             # print(f"match.groupdict()['branch_name']: {match.groupdict()['branch_name']}")
#             # print(f"match.groupdict()['branch_id']: {match.groupdict()['branch_id']}")
#             if match.groupdict()['branch_name'] == commit_id_or_branch:
#                 return match.groupdict()['branch_id']
#         # references_content = file.readlines()
#         # branches_data = references_content[1:]
#
#         # for branch_line in branches_data:
#             # name_and_id = branch_line.split('=')
#             # branch_name = name_and_id[0]
#             # branch_id = name_and_id[1].strip()
#             # if branch_name == commit_id_or_branch:
#             #     return branch_id
#     return commit_id_or_branch


def change_files_in_main_folder(commit_path: str, repository: Path) -> None:
    files_committed = get_all_files_in_directory_and_subs(commit_path, commit_path)
    for committed_file in files_committed:
        path_in_commit = os.path.join(commit_path, committed_file)
        with open(path_in_commit, 'r') as committed_file_h:
            content = committed_file_h.read()
        path_in_repository = os.path.join(repository, committed_file)
        with open(path_in_repository, "w") as original_file:
            original_file.write(content)


# בהתחלה עשיתי את הפונקציה כמו שמופיע למטה בהמשך ההערה, והערת לי שיש דרך הרבה יותר פשוטה להעתיק תיקיה
# ושיש פונקציה קיימת שיכולה לעזור לי, ולכן שינתי את הפונקציה כמו שמופיע למעלה.
# אבל ככה יש בעיה במקרה והתווסף קובץ חדש, ורוצים לעשות checkout לקומיט מלפני יצירת הקובץ,
# ואז בעצם בעידכון הקבצים בתיקיה צריך למחוק את הקובץ לחלוטין.
# לא הצלחתי לחשוב על פתרון פשוט לזה חוץ צלהשתמש בדרך המסורבלת יותר שאיתה התחלתי.
# אשמח לתובנות.
#
# def change_files_in_main_folder(repository: Path, commit_id: str) -> None:
#     commit_path = os.path.join(repository, '.wit', 'images', commit_id)
#     all_files_in_repository_and_sub_dirs = []
#     for (root, dirs, files) in os.walk(repository, topdown=True):
#         if '.wit' not in Path(root).parts:
#             for file in files:
#                 all_files_in_repository_and_sub_dirs.append(os.path.join(root, file))
#     all_files_in_commit_and_sub_dirs = []
#     for (root, dirs, files) in os.walk(commit_path, topdown=True):
#         for file in files:
#             all_files_in_commit_and_sub_dirs.append(os.path.join(root, file))
#     for c_file in all_files_in_commit_and_sub_dirs:
#         for r_file in all_files_in_repository_and_sub_dirs:
#             if Path(r_file).relative_to(repository) == Path(c_file).relative_to(commit_path):
#                 shutil.copy2(c_file, r_file)


def change_staging_area_folder(staging_area_path: str, commit_path: str):
    for file_or_dir in Path(staging_area_path).iterdir():
        if file_or_dir.is_file():
            file_or_dir.unlink()
        else:
            shutil.rmtree(file_or_dir)
    for file in Path(commit_path).iterdir():
        rel_path = Path(file).relative_to(commit_path)
        if file.is_file():
            shutil.copy2(file, Path(staging_area_path).joinpath(rel_path))
        else:
            shutil.copytree(file, Path(staging_area_path).joinpath(rel_path))
