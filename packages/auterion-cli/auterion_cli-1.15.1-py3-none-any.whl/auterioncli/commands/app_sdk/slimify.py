import argparse
import pathlib
import sys
import subprocess
import json
import tarfile
import os
import hashlib
import tempfile
import shutil


def run_docker_command(command, json_out=True):
    ret = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret.returncode != 0:
        print(ret.stderr.decode(), file=sys.stderr)
        raise RuntimeError(f'Command {str(command)} failed with exit code {ret.returncode}.')

    return json.loads(ret.stdout.decode()) if json_out else ret.stdout.decode()


def delete_from_tar_file(file, files_to_delete):
    temp_dir = tempfile.mkdtemp()
    with tarfile.open(file, 'r') as f:
        f.extractall(temp_dir)

    for delete_file in files_to_delete:
        os.remove(os.path.join(temp_dir, delete_file))

    with tarfile.open(file, 'w') as f:
        for file_to_add in pathlib.Path(temp_dir).glob('*'):
            f.add(file_to_add, file_to_add.relative_to(temp_dir), recursive=True)
    shutil.rmtree(temp_dir)


def error(msg, code=1):
    print(msg, file=sys.stderr)
    exit(code)


def get_file_size_mb(path):
    file_stats = os.stat(path)
    return file_stats.st_size / (1024*1024)


def get_base_image_layers(base_image, platform, cache_dir):
    cache_key = 'slimify_' + hashlib.sha1((base_image + '_' + platform).encode()).hexdigest() + '.json'
    if cache_dir is not None:
        cache_file = os.path.join(cache_dir, cache_key)
        if os.path.exists(os.path.join(cache_dir, cache_key)):
            print(f'.. Found cached base layer information for {base_image} {platform}')
            with open(cache_file, 'r') as f:
                return json.load(f)

    try:
        run_docker_command(['docker', 'pull', f'--platform={platform}', base_image], json_out=False)
    except:
        error(f'Failed to pull {platform} image for {base_image}. Aborting...')

    print(f'.. Pulled {base_image} for {platform}')
    print('> Inspecting image')
    try:
        ret = run_docker_command(['docker', 'inspect', base_image])
    except:
        error(f'Failed to inspect image {base_image}. Aborting..')

    architecture = platform.split('/')[1]
    assert(ret[0]['Architecture'] == architecture)
    assert(ret[0]['Os'] == 'linux')
    layers = ret[0]['RootFS']['Layers']
    print(f'.. Base image has {len(layers)} layers')

    if cache_dir is not None:
        cache_file = os.path.join(cache_dir, cache_key)
        with open(cache_file, 'w') as f:
            json.dump(layers, f)

    return layers


def slimify(save_image_path, base_image, platform, cache_dir=None):
    architecture = platform.split('/')[1]
    base_layers = get_base_image_layers(base_image, platform, cache_dir)
    with tarfile.open(save_image_path) as f:
        manifest_file = f.extractfile(f.getmember('manifest.json'))
        manifest = json.load(manifest_file)
        layer_entry_map = {}
        # we are not allowed to remove layers that appear multiple times in an image
        forbidden_layers = set()

        for image_information in manifest:
            seen_digests = set()
            image_layer_entries = image_information['Layers']
            config_name = image_information['Config']
            config_file = f.extractfile(f.getmember(config_name))
            config = json.load(config_file)
            assert(config['architecture'] == architecture)
            image_layers = config['rootfs']['diff_ids']
            for digest, file in zip(image_layers, image_layer_entries):
                if digest in seen_digests:
                    forbidden_layers.add(digest)
                seen_digests.add(digest)
                layer_entry_map[digest] = (file, file in f.getnames())

    removable_layers = set(layer_entry_map.keys()).intersection(set(base_layers)).difference(forbidden_layers)
    print(f'> Will remove {len(removable_layers)} from app image')
    for l in removable_layers:
        entry, exists = layer_entry_map[l]
        print(f'{l}: entry {entry} ' + ('' if exists else '(already deleted)'))
    files_to_remove = [layer_entry_map[l][0] for l in removable_layers if layer_entry_map[l][1]]

    file_size_pre = get_file_size_mb(save_image_path)
    delete_from_tar_file(save_image_path, files_to_remove)
    file_size_post = get_file_size_mb(save_image_path)
    print(f'.. All done. {file_size_pre:.2f} MB -> {file_size_post:.2f} '
          f'MB ({(file_size_post / file_size_pre * 100):.3f} %)')


def main():
    parser = argparse.ArgumentParser('Remove common common layers from a docker save')
    parser.add_argument('save_image', help='The saved docker artifact tar file')
    parser.add_argument('--base', '-b', help='The common base to remove layers from', required=True)
    args = parser.parse_args()
    slimify(args.save_image, args.base)


if __name__ == '__main__':
    main()

