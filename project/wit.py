from add import add
from branch import branch
from checkout import checkout
from commit import commit
from init import init
from graph import graph
from status import status

import sys


def is_command_correct(argv: list[str]) -> bool:
    if argv[1] in {'init', 'status', 'graph'}:
        return len(argv) == 2
    else:
        return len(argv) == 3


if sys.argv[1] == 'init':
    if is_command_correct(sys.argv):
        init()
    else:
        print(fr"Usage: python {sys.argv[0]} init")

elif sys.argv[1] == 'add':
    if is_command_correct(sys.argv):
        add(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} add <file_path>")

elif sys.argv[1] == 'commit':
    if is_command_correct(sys.argv):
        commit(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} commit MESSAGE")

elif sys.argv[1] == 'status':
    if is_command_correct(sys.argv):
        status()
    else:
        print(fr"Usage: python {sys.argv[0]} status")

elif sys.argv[1] == 'checkout':
    if is_command_correct(sys.argv):
        checkout(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} checkout <commit_id>")

elif sys.argv[1] == 'branch':
    if is_command_correct(sys.argv):
        branch(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} branch <NAME>")

elif sys.argv[1] == 'graph':
    if is_command_correct(sys.argv):
        graph()
    else:
        print(fr"Usage: python {sys.argv[0]} graph")
