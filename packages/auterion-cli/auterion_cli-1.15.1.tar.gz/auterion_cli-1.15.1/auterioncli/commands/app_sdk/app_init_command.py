import subprocess

import requests
from auterioncli.commands.command_base import CliCommand


class AppInitCommand(CliCommand):
    @staticmethod
    def help():
        return 'Initialize a new Auterion app repository'

    def needs_device(self, args):
        return False

    def __init__(self, config):
        pass

    def setup_parser(self, parser):
        pass

    def run(self, args):
        print("To start writing apps for AuterionOS, join the Auterion developer program.")
        print("You can get more resources on suite.auterion.com")
        print("Documentation: https://docs.auterion.com/")

