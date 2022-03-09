from graphviz import Digraph
from pathlib import Path
import re

from errors import WitError
from global_functions import get_repository_path, get_head_reference


regex = re.compile(r"^parent = (?P<commit_id>\w{20})$", flags=re.MULTILINE)


def graph_function():
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    current_commit_id = get_head_reference(repository)
    commit_id = current_commit_id
    dot = init_graph()
    wit_dir = repository / '.wit'
    images_path = wit_dir / 'images'
    while commit_id:
        commit_file = images_path / (commit_id + ".txt")
        create_node(commit_id, dot)
        commit_txt = commit_file.read_text()
        parent_id_match = regex.match(commit_txt)
        if parent_id_match:
            parent_id = parent_id_match.group('commit_id')
            create_node(parent_id, dot)
            dot.edge(commit_id, parent_id)
        commit_id = parent_id if parent_id_match else None
    dot.render(f'Graph {current_commit_id}', wit_dir, view=True, cleanup=True)


def create_node(commit_id: str, dot: Digraph) -> None:
    dot.node(commit_id, commit_id[:6] + '...')


def init_graph() -> Digraph:
    dot = Digraph(
        'graph_function',
        comment='Graph',
        node_attr={'color': 'lightblue2', 'style': 'filled', 'shape': 'circle'},
    )
    dot.attr(rankdir='LR', size='8,5')
    return dot
