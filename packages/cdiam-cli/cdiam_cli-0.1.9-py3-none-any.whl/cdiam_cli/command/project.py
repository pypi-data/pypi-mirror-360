from typing import Any

import click

from cdiam_cli import api
from cdiam_cli.schemas.base import MessageResponseError, MessageResponseSuccess


@click.group('project')
@click.pass_context
def project_cli(ctx):
    """
    This command group provides various commands to show and manage data related to projects.
    Use the subcommands under this group to interact with project effectively.
    """
    pass


@project_cli.command('list')
def list_all_project():
    """
        This command lists all the projects available in the system.
    """
    try:
        response: Any = api.api_action.run({"api": 'list_project'})
        output = MessageResponseSuccess(data=response)
    except Exception as e:
        output = MessageResponseError(error=str(e))
    click.echo(output.json())
