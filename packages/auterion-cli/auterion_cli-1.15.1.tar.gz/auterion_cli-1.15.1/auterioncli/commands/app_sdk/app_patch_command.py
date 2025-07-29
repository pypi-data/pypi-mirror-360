import requests
import os
import yaml
import subprocess
import tempfile
import shutil
import uuid
import sys
import argparse
import time
import filecmp
from pathlib import Path


from auterioncli.commands.command_base import CliCommand
from .app_build_command import AppBuildCommand
from .update import check_device_online
from ..utils import error, check_response_code


def eprint(msg):
    print(msg, file=sys.stderr)


def error(msg, code=1):
    eprint(msg)
    exit(code)


def run_command(commands, cwd='.', shell=False):
    print(f'> Executing \'{" ".join(commands)}\'')
    process = subprocess.Popen(commands, cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Read and print output line by line
    for line in process.stdout:
        print(line, end='')  # Print stdout line by line as it comes

    for line in process.stderr:
        print(line, end='')  # Print stderr line by line as it comes

    # Wait for the process to complete
    process.wait()

    # Check if the process exited with a non-zero code (indicating an error)
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, commands)

    return process.returncode


class AppPatchCommand(CliCommand):
    @staticmethod
    def help():
        return 'Patch a running app with updated files'

    def needs_device(self, args):
        if args.config:
            return False
        else:
            return True

    def __init__(self, config):
        self._live_patch_config_file_name = 'app-patch.yml'
        self._config = config
        self._device_address = config['device_address']
        self._apps_api_endpoint = f"http://{config['device_address']}/api/apps/v1.0"

    def setup_parser(self, parser):
        parser.add_argument('project_dir', help='Location of the project', nargs='?', default='.')
        parser.add_argument('-i', '--create-config', help=f'Create a {self._live_patch_config_file_name} config file', action='store_true')
        parser.add_argument('-c', '--config', help=f'Path to config file relative to project_dir (default: \'{self._live_patch_config_file_name}\')', nargs='?', default=self._live_patch_config_file_name)
        parser.add_argument('-s', '--simulation', help='Override target-platform to build simulation', action='store_true', default=False)
        parser.add_argument('-v' ,'--app-version', help='Override app version specified in auterion-app.yml file', default=None)
        parser.add_argument('--ip', help='device adress', nargs='?', default=None)

    def version(self, app_name):
        result = self._get_app(app_name)
        return result.get('version', 'unknown')

    def _get_app(self, app):
        data = check_response_code(
            requests.get(f'{self._apps_api_endpoint}/apps/{app}', cookies=self._config['cookies'],
                         headers=self._config['extra_headers']))
        try:
            body = data.json()
        except:
            body = {}
        if data:
            return body
        else:
            if "message" in body:
                error(body["message"])
            else:
                error(f"App {app} is not installed")

    def run(self, args):
        start = time.time()

        self._live_patch_config_file_name = args.config
        if args.ip:
            self._device_address = args.ip

        project_dir = Path(args.project_dir)

        # Check if auterion-app.yml exists
        app_meta_path = project_dir / 'auterion-app.yml'
        if not app_meta_path.exists():
            error(f'Error: No auterion-app.yml found in {project_dir}')

        # Load auterion-app.yml
        with open(app_meta_path, 'r') as f:
            meta = yaml.safe_load(f)

        # Create config file
        live_patch_config_path = project_dir / self._live_patch_config_file_name
        if args.create_config:
            # TODO prevent overwrite
            print(f'Creating app patch config at {live_patch_config_path}')
            with open(live_patch_config_path, 'w') as f:
                f.write('# app patch config for \`auterion-cli app patch\` command\n')
                f.write('services:\n')
                for service in meta.get('services', []):
                    f.write(f'  {service}:\n')
                    f.write(f'    files:\n')
                    f.write(f'#     - ./path/to/file\n')
                    f.write(f'#     - ...\n')
            exit(0)

        if args.app_version:
            print('.. Overriding app version to %s' % args.app_version)
            meta['app-version'] = args.app_version

        app_name = f'{meta["app-author"]}.{meta["app-name"]}'
        remote_app_version = self.version(app_name)
        local_app_version = f'{meta["app-version"]}'

        if remote_app_version != local_app_version:
            print(f'remote_app_version: {remote_app_version}')
            print(f'       app_version: {local_app_version}')
            error('Remote and local app version differ. Please run \'auterion-cli app build && auterion-cli app install build/*.auterionos\' first')
            exit(1)

        # check if upload config exists
        if not live_patch_config_path.exists():
            error(f'Error: No upload config found at {live_patch_config_path}\n' +
                    f'Run \'auterion-cli app patch --create-config\' to create a template config file')

        # Load upload-config
        with open(live_patch_config_path, 'r') as f:
            live_patch_config = yaml.safe_load(f)

        if live_patch_config is None:
            error(f'Error: Failed to parse upload config at {live_patch_config_path}')

        # Build the images without packing them
        build_args = args
        build_args.skip_packaging = True
        build_args.skip_docker_build = False
        build_args.no_cache = False
        build_args.app_version = meta['app-version']
        build_args.unversioned_file = False
        build_command = AppBuildCommand(self._config)
        build_command.run(args)


        for service in live_patch_config.get('services', []):
            container_name = f'{app_name}.{service}'
            image_name = f'{app_name}.{service}:{local_app_version}'
            image_name_tmp = f'{app_name}.{service}_tmp'
            files = live_patch_config['services'][service].get('files', [])
            if files is None:
                error('Patch config file does not define any files to patch! Aborting.')

            run_command(['docker', 'rm', '-f', image_name_tmp], cwd=project_dir)
            run_command(['docker', 'create', '--name', image_name_tmp, image_name], cwd=project_dir)
            run_command(['rm', '-rf', f'build/patch/{image_name_tmp}'], cwd=project_dir)
            run_command(['mkdir', '-p', f'build/patch/{image_name_tmp}'], cwd=project_dir)
            for file in files:
                # Recreate nested directory structure to file on local machine
                relative_path = os.path.dirname(file).lstrip('/')
                local_path = os.path.join(project_dir, 'build/patch', image_name_tmp, relative_path)
                os.makedirs(local_path, exist_ok=True)

                # Copy build files from container to local machine
                run_command(['docker', 'cp', f'{image_name_tmp}:{file}', f'{local_path}/'], cwd=project_dir)

            run_command(['docker', 'rm', '-f', image_name_tmp], cwd=project_dir)
            run_command(['ssh', f'root@{self._device_address}', f'rm -rf /tmp/{image_name_tmp} && mkdir -p /tmp/{image_name_tmp}'], cwd=project_dir)
            run_command(['scp', '-r', f'build/patch/{image_name_tmp}', f'root@{self._device_address}:/tmp/'], cwd=project_dir)
            run_command(['ssh', f'root@{self._device_address}', f'cd /tmp/{image_name_tmp} && tar -cf - . | docker exec -i {container_name} sh -c "tar -xf - -C /"'], cwd=project_dir)
            run_command(['ssh', f'root@{self._device_address}', f'docker commit {container_name} {container_name}:{local_app_version}'], cwd=project_dir)
            run_command(['ssh', f'root@{self._device_address}', f'rm -rf /tmp/{image_name_tmp}'])

        remore_settings_file_name = f'build/patch/{image_name_tmp}/remote_settings.default.env'
        run_command(['scp', f'root@{self._device_address}:/data/app/{app_name}/src/settings.default.env', remore_settings_file_name])

        if os.path.exists('settings.default.env'):
            settings_equal = filecmp.cmp('settings.default.env', remore_settings_file_name, shallow=False)

            if settings_equal:
                run_command(['auterion-cli', 'app', 'restart', app_name])
            else:
                run_command(['scp', 'settings.default.env', f'root@{self._device_address}:/data/app/{app_name}/src/settings.default.env'])
                run_command(['ssh', f'root@{self._device_address}', f'cd /data/app/{app_name}/src && docker compose down && docker compose up -d']) # to update env, container nees to be teared down once
        else:
            run_command(['auterion-cli', 'app', 'restart', app_name])


        end = time.time()
        runtime = end - start
        print(f"=== updating {app_name} took {int(runtime)} s ===")