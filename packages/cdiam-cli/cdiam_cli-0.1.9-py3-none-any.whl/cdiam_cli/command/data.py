from typing import Any

import click

from cdiam_cli import api
from cdiam_cli.schemas.base import MessageResponseError, MessageResponseSuccess


@click.group('data')
@click.pass_context
def data_cli(ctx):
    """
    This command group provides various commands to show and manage data related to projects.
    Use the subcommands under this group to interact with project effectively.
    """
    pass


@data_cli.command('list')
@click.argument('project_id')
def list_all_data(project_id: str):
    """
        This command lists all available data in given project id.
    """
    try:
        response: Any = api.api_action.run({
            "api": "list_data",
            "project_id": project_id
        })
        output = MessageResponseSuccess(data=response)
    except Exception as e:
        output = MessageResponseError(error=str(e))
    click.echo(output.json())
