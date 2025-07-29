import subprocess
import sys
import os
from auterioncli.commands.command_base import CliCommand
import tarfile
import tempfile
import shutil
import json


def error(msg):
    print(msg, file=sys.stderr)
    exit(1)

class AppInspectCommand(CliCommand):
    @staticmethod
    def help():
        return 'Inspects a .auterionos app file'

    def needs_device(self, args):
        return False

    def __init__(self, config):
        self._config = config

    def setup_parser(self, parser):
        parser.add_argument('app_file', help='The path to the .auterionos app file')
        parser.add_argument('--json', help='Output as JSON', action='store_true')

    def run(self, args):
        if not os.path.exists(args.app_file):
            error(f"App file {args.app_file} does not exist")

        # create temp dir
        temp_dir = tempfile.mkdtemp()
        with tarfile.open(args.app_file) as tar:
            tar.extract('header.tar.gz', temp_dir)

        with tarfile.open(os.path.join(temp_dir, 'header.tar.gz')) as tar:
            tar.extractall(temp_dir)

        meta_data_path = os.path.join(temp_dir, 'headers', '0000', 'meta-data')

        if not os.path.exists(meta_data_path):
            error(f"App file {args.app_file} does not contain necessary meta-data")

        with open(meta_data_path) as f:
            metadata = json.load(f)
        shutil.rmtree(temp_dir)

        # older CLI versions had the auterion metadata stored directly in the metadata
        # newer versions have it, as a json string, in the 'auterion-payload' key
        if 'auterion-metadata' in metadata:
            metadata = json.loads(metadata['auterion-metadata'])

        if args.json:
            print(json.dumps(metadata, indent=4))
            return

        if 'auterion-app-yml' not in metadata:
            error(f"App file {args.app_file} does not contain necessary meta-data. "
                  f"It's possible that this app file was created with an older version of auterion-cli.")

        auterion_app_yml = metadata['auterion-app-yml']
        print('Note: Run with --json to get machine-readable output')
        print('----------------------------------------------------------')
        print(f"App name: {auterion_app_yml.get('app-name', 'unknown')}")
        print(f"App version: {auterion_app_yml.get('app-version', 'unknown')}")
        print(f"App author: {auterion_app_yml.get('app-author', 'unknown')}")
        print(f"Target platform: {auterion_app_yml.get('target-platform', 'unknown')}")
        print(f"App API version: {auterion_app_yml.get('auterion-api-version', 'unknown')}")
        print(f"App base: {auterion_app_yml.get('auterion-app-base', 'unknown')}")

