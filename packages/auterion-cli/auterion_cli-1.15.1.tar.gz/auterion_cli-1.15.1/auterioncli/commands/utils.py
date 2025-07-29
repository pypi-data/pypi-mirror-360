from tqdm import tqdm
import requests
import sys

class Device:
    def __init__(self, address, version):
        self._address = address
        self._version = version

    @property
    def address(self):
        return self._address

    @property
    def version(self):
        return self._version


def check_response_code(response):
    if 200 <= response.status_code < 300:
        return response
    elif response.status_code == 401:
        error("Not authenticated to perform this action. Log into the device with 'auterion-cli device login' first.", 3)
    elif response.status_code == 403:
        error("Not authorized to perform this action", 3)
    elif response.status_code == 404:
        error("Not found", 5)
    elif 400 <= response.status_code < 500:
        error(f"Client Error: {response.status_code}\n||| " + response.text, 2)
    elif 500 <= response.status_code < 600:
        error(f"Server Error: {response.status_code}", 4)
    else:
        error(f"Unexpected HTTP status code: {response.status_code}", 1)


def download_file(url, destination_path, cookies, extra_headers):
    response = check_response_code(requests.get(url, stream=True, cookies=cookies, headers=extra_headers))
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(destination_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong while downloading..")


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def error(msg, code=1):
    eprint(msg)
    exit(code)
