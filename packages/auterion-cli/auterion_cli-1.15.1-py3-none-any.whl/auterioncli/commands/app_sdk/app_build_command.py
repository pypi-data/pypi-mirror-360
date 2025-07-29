import glob
import os
import shutil
import pathlib
import tarfile
import datetime
import yaml
import tempfile
import jsonschema
from auterioncli.commands.command_base import CliCommand
from auterioncli.commands.app_sdk.environment import \
    ensure_docker, ensure_mender_artifact, check_not_running_in_docker, check_not_running_on_skynode, \
    MENDER_CI_TOOLS_TAG
from auterioncli.commands.app_sdk.slimify import slimify
import subprocess
import collections.abc
import re
import copy
import sys
import json

DEVICE_ALIAS = {
    'ainode': 'jetson',
    'ainode-onx': 'jetsononx'
}

PLATFORM_ALIAS = {
    'dacnode': 'linux/arm64',
    'skynode': 'linux/arm64',
    'skynode-s': 'linux/arm64',
    'jetson': 'linux/arm64',
    'jetsononx': 'linux/arm64',
    'arkjetson': 'linux/arm64',
    'rb5': 'linux/arm64',
    'simulation': 'linux/amd64'
}


def deep_dict_update(target_dict, source_dict):
    for source_key, source_value in source_dict.items():

        # Check that the `compose-override` service key exists in the `services` section of the auterion-app.yml
        if source_key == "services" and isinstance(source_value, collections.abc.Mapping):
            for service_key in source_value.keys():
                if not service_key in target_dict["services"]:
                    error(f'Override service "{service_key}" not present in auterion-app.yml. Please fix.')

        if isinstance(source_value, collections.abc.Mapping):
            target_dict[source_key] = deep_dict_update(target_dict.get(source_key, {}), source_value)
        else:
            target_dict[source_key] = source_value
    return target_dict


def run_command(commands, cwd='.'):
    print(f'> Executing \'{" ".join(commands)}\'')
    result = subprocess.run(commands, cwd=cwd)
    return result.returncode


def error(msg, code=1):
    print(msg, file=sys.stderr)
    exit(code)


class AppBuildCommand(CliCommand):

    @staticmethod
    def help():
        return 'Build Auterion OS app in current directory'

    def needs_device(self, args):
        return False

    def __init__(self, config):
        self._temp_dir = None
        self._config = config

    def setup_parser(self, parser):
        parser.add_argument('project_dir', help='Location of the project', nargs='?', default='.')
        parser.add_argument('--skip-docker-build', help='Do not execute docker build step. Just package.', action='store_true')
        parser.add_argument('--skip-packaging', help='Do not create an AuterionOS app, just build the docker images and leave them in local docker.', action='store_true')
        parser.add_argument('-s', '--simulation', help='Override target-platform to build simulation', action='store_true', default=False)
        parser.add_argument('-v' ,'--app-version', help='Override app version specified in auterion-app.yml file', default=None)
        parser.add_argument('--unversioned-file', help='Do not include the app version in the app file name', action='store_true', default=False)
        parser.add_argument('--no-cache', help='Do not use docker cache when building images', action='store_true', default=False)

    def run(self, args):
        check_not_running_on_skynode(self._config.get('this_device_type', 'unknown'))

        self._temp_dir = tempfile.mkdtemp()
        meta = self._load_metadata(args)

        if args.simulation:
            print('.. Overriding target-platform. Building for simulation.')
            meta['target-platform'] = 'simulation'

        if args.app_version:
            print('.. Overriding app version to %s' % args.app_version)
            meta['app-version'] = args.app_version

        platform = self._extract_target_platform(meta)
        compose_cmd = ensure_docker(platform)
        ensure_mender_artifact()
        check_not_running_in_docker()

        self._verify_metadata(meta)

        image_path = self._generate_image(compose_cmd, args, meta)
        if args.skip_packaging:
            return

        if re.match('^v\d+$', meta['auterion-app-base']):
            v = meta['auterion-app-base']
            base_image_name = 'auterion/app-base:' + meta['auterion-app-base']
            slimify(image_path, base_image_name, platform, self._config['persistent_dir'])
            print('┌──────────────────────────────────────────────────────────────────────────────────────┐')
            print('│                                                                                      │')
            print('│  Your app requires the Auterion app-base-%s to be installed on your device.          │' % v)
            print('│                                                                                      │')
            print('│  Get app-base-%s.auterionos from Auterion Suite.                                     │' % v)
            print('│                                                                                      │')
            print('│  NOTE: The app-base has to be installed on the Skynode before you install your app.  │')
            print('│        You can install the app-base like an app:                                     │')
            print('│        `auterion-cli app install <path to app-base-%s.auterionos>`                   │' % v)
            print('│                                                                                      │')
            print('└──────────────────────────────────────────────────────────────────────────────────────┘')

        else:
            print(f'.. {meta["auterion-app-base"]} does not match a valid app-base version. Skipping slimify step.')
        compressed_image = self._compress_image(image_path)

        self._mender_package_app(args, meta, compressed_image)
        shutil.rmtree(self._temp_dir)

    @staticmethod
    def _verify_metadata(meta):
        schema_path = pathlib.Path(os.path.join(os.path.dirname(__file__), 'app-yml-spec'))
        resolver = jsonschema.validators.RefResolver(base_uri=f'{schema_path.as_uri()}/', referrer=True)
        try:
            jsonschema.validate(instance=meta, schema={'$ref': 'app-yml-spec.json'}, resolver=resolver)
        except jsonschema.ValidationError as e:
            error(f'Error: auterion-app.yml contains error. {e.message}')

    @staticmethod
    def _load_metadata(args):
        project_dir = args.project_dir
        meta_file = os.path.join(project_dir, 'auterion-app.yml')

        if not os.path.exists(meta_file):
            error(f'File \'{meta_file}\' does not exist. App structure invalid. Aborting...')

        with open(meta_file, 'r') as f:
            meta = yaml.safe_load(f)

        if 'app-author' not in meta:
            error(f'{meta_file} does not contain `app-author` key. This field should contain a reverse-domain of the'
                  f' entity that authored the app, e.g. `com.auterion`')
        return meta

    def _extract_target_devices(self, meta):
        target_devices = [meta['target-platform']] \
            if isinstance(meta['target-platform'], str) else meta['target-platform']
        target_devices = [DEVICE_ALIAS.get(d, d) for d in target_devices]
        for d in target_devices:
            if d not in PLATFORM_ALIAS:
                error(f'Target platform "{d}" is not supported. Must be one of: {", ".join(PLATFORM_ALIAS.keys())}. Aborting.')
        return target_devices

    def _extract_target_platform(self, meta):
        target_devices = self._extract_target_devices(meta)
        target_platforms = [PLATFORM_ALIAS.get(d, d) for d in target_devices]
        if len(set(target_platforms)) > 1:
            error('Targets have multiple architectures. Aborting.')
        return target_platforms[0]

    def _compose_for_building_from_meta(self, meta):
        api_version = meta['auterion-api-version']
        assert 0 <= api_version <= 6, f'Auterion API version {api_version} is not supported by this ' \
                                      f'version of auterion-cli. Supported API versions are 0 to 6.'

        compose = {}
        if api_version == 0:
            compose = {
                **meta['compose']
            }
        elif api_version >= 1:
            compose = {
                'services': {}
            }
            for name, service_config in meta['services'].items():
                compose['services'][name] = {}
                if 'build' in service_config:
                    compose['services'][name]['build'] = {
                        "context": service_config['build']
                    }
                    if 'build-args' in service_config:
                        compose['services'][name]['build']['args'] = service_config['build-args']
                elif 'image' in service_config:
                    compose['services'][name]['image'] = service_config['image']

            # api version 1 still allows for dict update
            if 'compose-override' in meta:
                deep_dict_update(compose, meta['compose-override'])

        for name, service in compose['services'].items():
            fully_qualified_name = meta['app-author'] + '.' + meta['app-name'] + '.' + name
            if 'image' not in service:
                service['image'] = fully_qualified_name + ':' + meta['app-version']
            service['container_name'] = fully_qualified_name
            service['platform'] = self._extract_target_platform(meta)
        return compose

    def _generate_image(self, compose_cmd, args, meta):
        # Generate build dir
        project_dir = args.project_dir
        build_dir = os.path.join(project_dir, 'build')
        if not os.path.exists(build_dir):
            os.mkdir(build_dir)

        target_file = os.path.join(build_dir, meta['app-author'] + '.' + meta['app-name'] + '.tar')

        # generate a minimal docker-compose file in temp dir for building using docker-compose
        # (don't use self._temp_dir, as podman-compose sets cwd to that directory)
        compose_file = os.path.join(args.project_dir, 'build-compose.yml')
        compose = self._compose_for_building_from_meta(meta)
        with open(compose_file, 'w') as f:
            yaml.dump(compose, f)

        if not args.skip_docker_build:
            # Just export the required images from the local docker
            target_platform = self._extract_target_platform(meta)

            build_command = compose_cmd + ['-f', compose_file, 'build']
            if args.no_cache:
                build_command.append('--no-cache')
            ret = run_command(build_command, cwd=args.project_dir)

            if ret != 0:
                error("------------------------------------------------------\n"
                      "Docker build failed. \n"
                      "Temporary `build-compose.yml` file left in tree. \n\n"
                      "This is most likely not a problem with auterion-cli.\n"
                      "To debug the build without auterion-cli, run \n"
                      f"{' '.join(build_command)}")
            os.remove(compose_file)

            built_images = [v['image'] for k, v in compose['services'].items() if 'build' in v]
            for image in built_images:
                # Make sure that we correctly tag all images with the docker.io prefix. This is not
                # guaranteed on alternative runtimes such as podman
                print('retagging...')
                ret = run_command(['docker', 'tag', image, 'docker.io/' + image], cwd=project_dir)
                if ret != 0:
                    error(f'Failed to retag {image} to docker.io/{image}. Aborting.')
            built_images = ['docker.io/' + image for image in built_images]

            non_built_images = [v['image'] for k, v in compose['services'].items() if 'build' not in v]
            if len(non_built_images) > 0:
                for image in non_built_images:
                    # check if available locally
                    ret = subprocess.run(['docker', 'inspect', image], stdout=subprocess.PIPE)
                    if ret.returncode == 0:
                        inspect_result = json.loads(ret.stdout.decode())
                        architecture = inspect_result[0]['Architecture']
                        if architecture == target_platform.split('/')[1]:
                            print(f'Image {image} is available locally')
                            continue

                    print(f'Image {image} is not available locally. Trying to pull')
                    ret = run_command(['docker', 'pull', '--platform', target_platform, image])
                    if ret != 0:
                        error(f"Failed to pull {image}, which you specified \n"
                              "as a pre-built image. Aborting.")
            images = built_images + non_built_images
        else:
            images = [v['image'] for k, v in compose['services'].items()]

        print('According to docker-compose, we have the following images:')
        for image in images:
            print(f'- {image}')

        if (args.skip_packaging):
            print('Skipping packaging of images. Leaving images in docker:')
            for image in images:
                print(f'- {image}')
            return None

        print('Packaging those images...')
        if os.path.isfile(target_file):
            os.remove(target_file)
        ret = run_command(['docker', 'save'] + images + ['-o', target_file], cwd=project_dir)
        if ret != 0:
            error(f'Failed to package images to {target_file}. Docker save command failed. Aborting.')

        return target_file

    def _compress_image(self, image):
        compressor = 'pigz' if shutil.which('pigz') else 'gzip'
        if compressor == 'gzip':
            warning_message = """\
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ WARNING: pigz not found!                                                               │
│                                                                                        │
│ pigz is a parallel implementation of gzip and can significantly speed up compression.  │
│                                                                                        │
│ Consider installing it using:                                                          │
│   • Debian/Ubuntu: sudo apt install pigz                                               │
│   • macOS: brew install pigz                                                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
            """
            print(warning_message)
        ret = run_command([compressor, image])
        if ret != 0:
            error(f'Failed to compress image {image}. Aborting.')
        p = pathlib.Path(image + '.gz')
        target_name = p.with_suffix('').with_suffix('.image')
        p.rename(target_name)
        return str(target_name)

    def _generate_legacy_app_file(self, meta, slug, app_file):
        # add default settings for compose
        compose = self._compose_for_building_from_meta(meta)
        app_dict = copy.deepcopy(compose)
        for name, service in app_dict['services'].items():
            if 'restart' not in service:
                service['restart'] = 'unless-stopped'
            if 'network_mode' not in service:
                service['network_mode'] = 'host'
            if 'volumes' not in service:
                service['volumes'] = [f'/data/app/{slug}/data:/data']
            if 'environment' not in service:
                service['environment'] = ['PYTHONUNBUFFERED=1']
            if 'env_file' not in service:
                service['env_file'] = ['settings.default.env', 'settings.user.env']

            # older docker-compose get confused about the platform and build tags
            if 'platform' in service:
                del service['platform']
            if 'build' in service:
                del service['build']

        with open(app_file, 'w') as fo:
            yaml.dump(app_dict, fo)

    def _mender_package_app(self, args, meta, image_file):
        if not os.path.exists(image_file):
            error(f'Image {image_file} does not exist. Nothing to package. Aborting..')

        version = meta['app-version']
        name = meta['app-name']

        slug = meta['app-author'] + '.' + meta['app-name']

        target_devices = self._extract_target_devices(meta)
        target_devices_args = []
        for d in target_devices:
            target_devices_args += ['-t', d]

        filename_base = slug
        if not args.unversioned_file:
            filename_base += '-' + meta['app-version']
        if 'simulation' in target_devices:
            filename_base += '-simulation'
        out_file = os.path.join(args.project_dir, 'build', filename_base + '.auterionos')

        content_for_packaged_meta_file = copy.deepcopy(meta)
        if meta['auterion-api-version'] <= 4:
            # legacy AuterionOS do strictly check for the target platform in schema check. Fake the target platform
            # in the bundled auterion-app.yml file, so that the schema check passes
            content_for_packaged_meta_file['target-platform'] = ['skynode']

        # write meta content to a new auterion-app.yml file to be bundled in the app
        meta_file = os.path.join(self._temp_dir, 'auterion-app.yml')
        with open(meta_file, 'w') as f:
            yaml.dump(content_for_packaged_meta_file, f)

        version_file = os.path.join(self._temp_dir, 'version')
        with open(version_file, 'w') as f:
            f.write(version)

        settings_file = os.path.join(args.project_dir, 'settings.default.env')

        # Add ROS 2 message files
        temp_msg_tar_file = os.path.join(self._temp_dir, 'logging-msg-files.tar')
        if 'logging' in meta:
            temp_msg_path = os.path.join(self._temp_dir, 'logging-msg-files')
            logging_meta = meta['logging']
            has_msg_files = False
            msg_paths = logging_meta.get('msg-paths', []) # msg-paths can be a list of strings or a string
            if isinstance(msg_paths, str):
                msg_paths = [msg_paths]
            for msg_path_base in msg_paths:
                msg_path = os.path.join(args.project_dir, msg_path_base, 'msg')
                if not os.path.isdir(msg_path):
                    error(f'Message path "{msg_path}" does not exist')

                print(f'Adding messages in {msg_path}')
                pkg_name = os.path.basename(msg_path_base)
                target_dir = os.path.join(temp_msg_path, pkg_name, 'msg')
                os.makedirs(target_dir, exist_ok=True)
                for msg_file in glob.glob(os.path.join(msg_path, '*.msg')):
                    shutil.copy(msg_file, target_dir)
                    has_msg_files = True
            if has_msg_files:
                with tarfile.open(temp_msg_tar_file, 'w') as logging_msg_tar:
                    logging_msg_tar.add(temp_msg_path, recursive=True, arcname='')

        if not os.path.exists(settings_file):
            settings_file = os.path.abspath(os.path.join(self._temp_dir, 'settings.default.env'))
            # create empty file
            pathlib.Path(settings_file).touch()

        # create empty user settings file for AuterionOS < 2.7
        user_settings_file = os.path.abspath(os.path.join(self._temp_dir, 'settings.user.env'))
        pathlib.Path(user_settings_file).touch()

        file_args = [
            '-f', os.path.abspath(meta_file),
            '-f', os.path.abspath(image_file),
            '-f', os.path.abspath(version_file),
            '-f', os.path.abspath(settings_file),
            '-f', os.path.abspath(user_settings_file)
        ]
        if os.path.exists(temp_msg_tar_file):
            file_args += ['-f', os.path.abspath(temp_msg_tar_file)]

        if meta['auterion-api-version'] < 2:
            app_file = os.path.join(self._temp_dir, 'app.yml')
            self._generate_legacy_app_file(meta, slug, app_file)
            file_args += ['-f', app_file]

        pathlib.Path(settings_file).touch()

        # Create mender package metadata
        mender_package_metadata_auterion_metadata = {
            'build-time': datetime.datetime.now().isoformat(),
            'build-platform': self._config.get('platform', 'UNKNOWN'),
            'cli-version': self._config.get('version', 'UNKNOWN'),
            'auterion-app-yml': meta
        }
        # We have to add the auterion payload as a string, since mender metadata does not allow arbitrary JSON
        mender_package_metadata = {
            'auterion-metadata': json.dumps(mender_package_metadata_auterion_metadata)
        }
        mender_package_metadata_file = os.path.join(self._temp_dir, 'mender-package-metadata.json')
        with open(mender_package_metadata_file, 'w') as f:
            json.dump(mender_package_metadata, f)

        ret = run_command([
            'docker',
            'run',
            '--privileged',
            '--rm',
            '--mount',
            f'type=bind,source={os.path.abspath(args.project_dir)},target={os.path.abspath(args.project_dir)}',
            '--mount',
            f'type=bind,source={os.path.abspath(self._temp_dir)},target={os.path.abspath(self._temp_dir)}',
            MENDER_CI_TOOLS_TAG,
            'mender-artifact', 'write', 'module-image',
            '-o', os.path.abspath(out_file),
            '-T', 'docker',
            '-n', slug + ':' + version,
            '--software-filesystem', 'docker-app',
            '--software-name', slug,
            '--software-version', version,
            '--meta-data', os.path.abspath(mender_package_metadata_file),
        ] + target_devices_args + file_args)

        if ret != 0:
            error('Packaging step failed. Aborting.')

        # get rid of image file
        os.unlink(image_file)

