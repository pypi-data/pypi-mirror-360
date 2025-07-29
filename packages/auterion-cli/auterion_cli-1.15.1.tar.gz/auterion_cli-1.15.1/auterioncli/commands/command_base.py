import argparse


class CliCommand:
    @staticmethod
    def help():
        return None

    def setup_parser(self, parser: argparse.ArgumentParser):
        raise NotImplemented

    def run(self, args):
        raise NotImplemented

    def needs_device(self, args):
        return True

    def handle_exception(self, exception: Exception):
        raise exception
