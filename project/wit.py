import click

from project.add import add_function
from project.branch import branch_function
from project.checkout import checkout_function
from project.commit import commit_function
from project.graph import graph_function
from project.init import init_function
from project.merge import merge_function
from project.status import status_function


@click.group()
def cli():
    pass


@cli.command()
def init():
    """Create a wit folder in the directory."""
    init_function()


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def add(path):
    """Add file or folder to staging area."""
    add_function(path)


@cli.command()
@click.argument("message")
def commit(message):
    """Save image of current files in staging area.
    Save a message.
    """
    commit_function(message)


@cli.command()
def status():
    """Show the status of files in directory."""
    status_function()


@cli.command()
@click.argument("commit_id_or_branch")
def checkout(commit_id_or_branch):
    """Switch to another commit or branch, which will be activated."""
    checkout_function(commit_id_or_branch)


@cli.command()
@click.argument("branch_name")
def branch(branch_name):
    """Create a new branch."""
    branch_function(branch_name)


@cli.command()
def graph():
    """Show graph of commits from current commit to the first."""
    graph_function()


@cli.command()
@click.argument("branch_name")
def merge(branch_name):
    """Merge the files in the current commit with the branch."""
    merge_function(branch_name)


if __name__ == "__main__":
    cli()
