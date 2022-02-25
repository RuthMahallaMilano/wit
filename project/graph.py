import graphviz
from pathlib import Path

from add import get_repository_path
from errors import WitError


def graph():
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")

#
# dot = graphviz.Digraph(comment='The Round Table')
#
# dot.node('A', 'King Arthur')
# dot.node('B', 'Sir Bedevere the Wise')
# dot.node('L', 'Sir Lancelot the Brave')
# dot.edges(['AB', 'AL'])
# dot.edge('B', 'L', constraint='false')
#
# dot.render('FileName', view=True)