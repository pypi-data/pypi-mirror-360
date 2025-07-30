import click
import os
from os.path import expanduser
import json


def get_path_settings():
    home = expanduser("~")
    return os.path.join(home, ".cdiam_cli")


def read_api_endpoint():
    if not os.path.exists(get_path_settings()):
        raise Exception("Run save-settings first")
    with open(get_path_settings(), "r") as f:
        settings = json.load(f)
        if "endpoint" not in settings:
            raise Exception(
                "Cannot found endpoint setting. Please run save-settings first"
            )
        return settings["endpoint"]


def read_api_token():
    if not os.path.exists(get_path_settings()):
        raise Exception("Run save-settings first")
    with open(get_path_settings(), "r") as f:
        settings = json.load(f)
        if "token" not in settings:
            raise Exception(
                "Cannot found token setting. Please run save-settings first"
            )
        return settings["token"]


class HiddenPassword(object):
    def __init__(self, password=""):
        self.password = password

    def __str__(self):
        return "*" * len(self.password)


@click.command()
def save_token():
    """This api save your endpoint and your token in your machine"""
    endpoint = click.prompt(
        "Please enter the server endpoint E.g. https://c-diam.com/api", type=str
    )
    value = click.prompt("Please enter the token", type=HiddenPassword, hide_input=True)
    with open(get_path_settings(), "w") as f:
        json.dump(
            {
                "endpoint": endpoint,
                "token": value.password,
            },
            f,
        )
    print(f"Save settings at {get_path_settings()}")
