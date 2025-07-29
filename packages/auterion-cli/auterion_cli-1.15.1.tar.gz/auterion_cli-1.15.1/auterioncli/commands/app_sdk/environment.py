import subprocess
import json
import sys
import os

import requests


def error(msg, code=1):
    print('Error: ' + msg, file=sys.stderr)
    exit(code)


def try_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return 0, result.stdout.decode()
        else:
            return result.returncode, 'Command ' + ' '.join(command) + ' failed on this system.'
    except FileNotFoundError:
        return 2, 'Command ' + ' '.join(command) + ' not found on this system.'


ARM64_TEST_IMAGE = 'arm64v8/alpine:3.15'

def ensure_docker(platform):

    code, result = try_command(['docker', 'version', '--format', '{{json .}}'])
    if code != 0:
        error('Docker not working on this system. Make sure docker is installed and runnable')

    res = json.loads(result)
    server_version = 'N/A'
    if 'Server' in res:
        server_version = res['Server']['Version']
    client_version = res['Client']['Version']
    print(f'.. Found docker client {client_version}, server {server_version}')

    client_version_components = client_version.split('.')

    # Try podman-compose, fall back to docker compose
    compose_cmd = ['podman-compose']
    is_podman = True

    code, _ = try_command(compose_cmd + ['version'])
    if code != 0:
        is_podman = False
        compose_cmd = ['docker', 'compose']
        code, _ = try_command(compose_cmd + ['version'])
        if code != 0:
            error('Docker compose plugin not found on this system. Make sure you have docker compose installed. \n'
                  'E.g. on ubuntu, you can install it with \'sudo apt-get install docker-compose-plugin\'')
    print('.. Found docker compose plugin')

    if not is_podman:
        if len(client_version_components) <= 0 or int(client_version_components[0]) < 20:
            error('auterion-cli needs at least docker client 20.\nMake sure to update the docker version on your system'
                  'using your package manager. \n'
                  'For ubuntu, find more information on https://docs.docker.com/engine/install/ubuntu/ ')

    if "arm64" not in platform:
        print('.. Docker will not need to run arm64 containers')
        return compose_cmd

    # Check that docker can run arm64 containers
    code, result = try_command(['docker', 'inspect', '--type=image', ARM64_TEST_IMAGE])
    if code != 0:
        print('> Pulling arm64 test image ...')
        code, result = try_command(['docker', 'pull', 'docker.io/' + ARM64_TEST_IMAGE])
        if code != 0:
            error(f'Could not pull {ARM64_TEST_IMAGE} image from docker hub. Exiting.')

    code, result = try_command(['docker', 'run', '--rm', '--platform=linux/arm64', ARM64_TEST_IMAGE,
                                'uname', '-m'])
    if code != 0 or ('aarch64' not in result and 'arm64' not in result):
        error('Docker cannot run arm64 containers. \n'
              'Make sure you have docker installed and configured to run arm64 containers.\n'
              'You can check this by running \'docker run --rm --platform=linux/arm64 ubuntu:latest uname -m\'\n'
              'For docker setup instructions find more information on  https://docs.auterion.com/app-development/resources/auterion-cli')
    print('.. Docker can run arm64 containers')

    return compose_cmd


MENDER_CI_TOOLS_TAG = 'auterion/mender-ci-tools:latest'


def _test_mender_artifact():
    code, res = try_command(['docker', 'run', '--rm', MENDER_CI_TOOLS_TAG, 'mender-artifact', '--version'])
    if code == 0:
        print('.. Found mender artifact ' + res)
        return True
    return False


def ensure_mender_artifact():

    # check if exists locally
    code, result = try_command(['docker', 'inspect', '--type=image', MENDER_CI_TOOLS_TAG])
    if code != 0:
        print('> Pulling mender ci-tools ...')
        code, result = try_command(['docker', 'pull', 'docker.io/' + MENDER_CI_TOOLS_TAG])
        if code != 0:
            error(f'Could not pull {MENDER_CI_TOOLS_TAG} image from docker hub. Exiting.')

    if not _test_mender_artifact():
        error(f'Error: Failed to execute mender artifact in image {MENDER_CI_TOOLS_TAG}. Aborting.')


def check_not_running_in_docker():
    if os.path.exists('/.dockerenv'):
        print('Detected to be running inside docker. The app build command needs to to execute docker commands'
              'that are only possible from the host system.', file=sys.stderr)
        error('Error: auterion-cli app build should not be run inside a docker container. Exiting.')


def check_not_running_on_skynode(this_device_type):
    if this_device_type.startswith('auterion'):
        error('This command is not supported on Skynode. \n '
              'Build your app on your computer and then use the \'app install\' command to install it on your Skynode.')
