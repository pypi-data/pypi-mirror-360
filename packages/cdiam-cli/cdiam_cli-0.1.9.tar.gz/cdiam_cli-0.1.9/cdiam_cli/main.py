import click

from cdiam_cli import api
from cdiam_cli.command import data, project


@click.group()
@click.pass_context
def main_group(ctx):
    pass


# Groups
main_group.add_command(project.project_cli)
main_group.add_command(data.data_cli)

# Single command
main_group.add_command(api.call_api)
main_group.add_command(api.save_token)


if __name__ == "__main__":
    main_group()
