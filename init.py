# upload 170
import os
import sys


def init():
    cwd = os.getcwd()
    wit_path = os.path.join(cwd, '.wit')
    os.mkdir(wit_path)
    os.mkdir(os.path.join(wit_path, 'images'))
    os.mkdir(os.path.join(wit_path, 'staging_area'))


def is_init_command_correct(argv):
    return len(argv) == 2


if sys.argv[1] == 'init':
    if is_init_command_correct(sys.argv):
        init()
    else:
        print(r"Usage: python C:\Users\israe\PycharmProjects\wit_project\wit.py init")
