#! /usr/bin/env python3
import argparse
import json
import os
import signal
import sys

import requests
import time
import enum
from datetime import datetime
try:
    from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
    from tqdm import tqdm
except ImportError as e:
    print("Modules tqdm and requests-toolbelt are missing")
    exit(1)

UPDATE_ENDPOINT_BASE="http://{}/api/local-updater"
TIMEOUT = 1800  # 30 minutes

class ExitCode(enum.Enum):
    SUCCESS = 0
    ARTIFACT_NOT_FOUND = 1
    UPDATE_FAILED = 2
    FMU_UPDATE_FAILED = 3
    DEVICE_NOT_CONNECTED = 4
    TIMEOUT = 5
    INCOMPATIBLE_API = 6
    CANCELLED = 10
    INVALID_ARTIFACT = 11
    REQUEST_API_VERSION = 99

def get_api_version(url):
    try:
        response = requests.get(f"{url}/version",  timeout=5)
        if response and "version" in response.json():
            return response.json()["version"]
        elif response.status_code == 404:
            # The version route is not implemented in v1.0
            return "v1.0"
        else:
            return None
    except:
        return None

def cancel_update(url):
    print("Cancelling update...")
    try:
        response = requests.post(f"{url}/rollback")
        if response.status_code == 200:
            print("Update cancellation requested...")
        elif response.status_code == 404:
            print("Cancellation endpoint not found for your current AOS version: update will proceed on the connected device.")
            sys.exit(0)
        else:
            print(f"Cancel request received response: {response}")
            sys.exit(0)
    except Exception as e:
        print(f"Failed to send cancel update request: {e}")
        sys.exit(0)

    is_final_state = False
    while(not is_final_state):
        is_final_state, code, _, _ = get_device_status(url, verbose=False)
        time.sleep(0.1)

    if code == ExitCode.CANCELLED:
        print("Update cancelled successfully")
    elif code == ExitCode.SUCCESS:
        print("Update completed succesfully before cancellation triggered")
    else:
        print(f"Update finished with code: {code}. Exiting.")

    sys.exit(0)

def refresh_progress_bar(monitor):
    if monitor.finished:
        return
    if monitor.last_bytes_read is None:
        monitor.progress_bar.update(monitor.bytes_read)
    else:
        monitor.progress_bar.update(monitor.bytes_read-monitor.last_bytes_read)
    monitor.last_bytes_read = monitor.bytes_read
    percentage = float(monitor.last_bytes_read) / float(monitor.total_size)
    if percentage > 1.0:
        monitor.finished = True
        monitor.progress_bar.close()
        print("Waiting for the device to complete the installation")

def upload_artifact(url, file_path, cookies, extra_headers):
    filename = os.path.basename(file_path) or "unknown.auterionos"
    e = MultipartEncoder(fields={'file': (filename, open(file_path,"rb"), 'application/octet-stream')})
    m = MultipartEncoderMonitor(e, refresh_progress_bar)
    m.last_bytes_read = None
    m.total_size = os.path.getsize(file_path)
    m.progress_bar = tqdm(desc="Uploading artifact", unit_scale=True, total=m.total_size)
    m.finished = False
    try:
        if not extra_headers:
            extra_headers = {}
        extra_headers['Content-Type'] = m.content_type

        metadata = {
            'installation_id': datetime.now().strftime('%Y%m%d%H%M%S')
        }

        extra_headers['X-Metadata'] = json.dumps(metadata)

        # Request update cancellation on user interrupt 
        signal.signal(signal.SIGINT, lambda signal, frame: cancel_update(url))




        
        response = requests.post("{}/update".format(url), data=m, cookies=cookies, headers=extra_headers)

        if response.status_code == 200:
            print("The device has been updated successfully")
            exit(0)

        elif response.status_code == 401:
            print("Not authenticated to perform this action", file=sys.stderr)
            print("Log into the device with 'auterion device login' first.", file=sys.stderr)
            exit(1)

        elif 400 <= response.status_code <= 500:
            data = response.json()
            if "message" in data:
                print(data['message'], file=sys.stderr)
            else:
                print("Failed to update device", file=sys.stderr)
            exit(1)

        elif response.status_code == 504:  # initial request timed out
            return True, "Installation taking longer, switching to polling.."
        else:
            try:
                data = response.json()
                if "logs" in data:
                    print("Error logs:", file=sys.stderr)
                    for line in data['logs'].replace("\\n", "\n").split('\n'):
                        print(' |  ' + line, file=sys.stderr)
                message = "Failed to install"
                if "message" in data:
                    message = data['message']
            except:
                message = "Failed to install. Response code: {}".format(response.status_code)
            return False, message
    except Exception as e:
        print(e)
        m.progress_bar.close()
        return False, e


def check_device_online(url):
    try:
        if requests.get("{}/ping".format(url)):
           return True
        if requests.get("{}/v1.0/ping".format(url)):
           return True
    except:
        try:
            if requests.get("{}/v1.0/ping".format(url)):
                return True
        except:
            return False
    return False

def print_device_status(status):
    if status == "INSTALLING":
        print("Waiting for the device to complete the installation")
    elif status == "INSTALLED":
        print("Waiting for the device to reboot")
    elif status == "REBOOTING":
        print("Device is rebooting")
    elif status == "REBOOTED":
        print("Device rebooted")
    elif status == "VERIFICATION":
        print("Update verification")
    elif status == "FMU_UPDATE":
        print("Update FMU")
    elif status == "FMU_UPDATE_SUCCEED":
        print("FMU updated successfully")
    elif status == "CUSTOM_APP_INSTALL":
        print("Installing custom apps")
    elif status == "FMU_UPDATE_FAILED":
        print("FMU update failed")
    elif status == "REPARTITIONING":
        print("Device is being repartitioned")
    elif status == "SUCCEED":
        print("The device has been updated successfully")
    elif status == "APP_INSTALL_SUCCEED":
        print("Application has been installed successfully")
    elif status == "APP_INSTALL_FAILED":
        print("Application installation failed.")
    elif status == "FAILED":
        print("Update verification failed. The system has been rollbacked")
    elif status == "NEED_POWER_CYCLE":
        print("The device has been updated successfully, you need to powercycle your drone to complete the update.")
    elif status == "CANCELLED":
        print("Update has been cancelled")
    elif status == "INVALID_ARTIFACT":
        print("Update has been cancelled: Artifact is invalid")

def get_device_status(url, reboot_counter=0, last_status=None, verbose=True):
    status = None
    try:
        response = requests.get("{}/status".format(url), timeout=1)

        if response.status_code == 404:
            return False, ExitCode.REQUEST_API_VERSION, None, reboot_counter

        # In local-updater PR #77, the status of the update was moved from the status field to the status_key field.
        # This change was required to ensure compatibility with task-monitor's status schema.
        # The following line extract the status in a manner that is compatible with both versions of local-updater.
        # Order is important, as the newer version uses the status field for a different purpose.
        status = response.json().get("status_key") or response.json().get("status")
    except:
        if reboot_counter > 5:
            status = "REBOOTING"
        else:
            status = last_status
            reboot_counter += 1
    # if status == "UPLOADING":
    #     # We do nothing
    code = None
    if last_status != status:
        if last_status == "REBOOTING":
            # Force to request the API
            return False, ExitCode.REQUEST_API_VERSION, None, reboot_counter
        elif status == "FMU_UPDATE_FAILED":
            code = ExitCode.FMU_UPDATE_FAILED
        elif status == "SUCCEED":
            code = ExitCode.SUCCESS
        elif status == "APP_INSTALL_SUCCEED":
            code = ExitCode.SUCCESS
        elif status == "APP_INSTALL_FAILED":
            code = ExitCode.UPDATE_FAILED
        elif status == "FAILED":
            code = ExitCode.UPDATE_FAILED
        elif status == "NEED_POWER_CYCLE":
            code = ExitCode.SUCCESS
        elif status == "CANCELLED":
            code = ExitCode.CANCELLED
        elif status == "INVALID_ARTIFACT":
            code = ExitCode.INVALID_ARTIFACT
        if verbose:
            print_device_status(status)

    return code != None, code, status, reboot_counter

def update_failed(message, url):
    _, code, _, _ = get_device_status(url)
    print(message)
    if code == None:
        code = ExitCode.UPDATE_FAILED
    exit(code.value)


def do_update(artifact_path, device_ip, cookies, extra_headers):
    UPDATE_ENDPOINT = UPDATE_ENDPOINT_BASE.format(device_ip)
    if artifact_path is None:
        print("Artifact path is missing")
        exit(1)
    print("Looking for the update artifact")
    if os.path.exists(artifact_path):
        print("Check if your device is online...")
        if check_device_online(UPDATE_ENDPOINT):
            version = get_api_version(UPDATE_ENDPOINT)
            if version is None:
                print("Your device is not connected")
                exit(4)
            url = "{}/{}".format(UPDATE_ENDPOINT, version)
            print("API: {}".format(version))
            succeed, message = upload_artifact(url, artifact_path, cookies, extra_headers)
            if succeed:
                final_state = False
                code = 0
                reboot_counter = 0
                last_status = None
                start = datetime.now()
                while not final_state and (datetime.now() - start).seconds <= TIMEOUT:
                    time.sleep(1)
                    final_state, code, last_status, reboot_counter = get_device_status(url, reboot_counter, last_status)
                    if code == ExitCode.REQUEST_API_VERSION:
                        # We might have rebooted on a previous version of local-updater
                        version = get_api_version(UPDATE_ENDPOINT)
                        if version is None:
                            print("Failed to get API version")
                            exit(ExitCode.INCOMPATIBLE_API.value)
                        url = "{}/{}".format(UPDATE_ENDPOINT, version)
                        print("API: {}".format(version))
                if (datetime.now() - start).seconds > TIMEOUT:
                    print("Update timeout")
                    exit(ExitCode.TIMEOUT.value)
                else:
                    exit(code.value)
            else:
                update_failed(message, url)
        else:
            print("Your device is not connected")
            exit(ExitCode.DEVICE_NOT_CONNECTED.value)
    else:
        print("Update artifact not found")
        exit(ExitCode.ARTIFACT_NOT_FOUND.value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", help="artifact path")
    parser.add_argument("--device-ip", default="10.41.1.1", help="artifact path")
    args = parser.parse_args()
    artifact_path = args.artifact
    device_ip = args.device_ip

    do_update(artifact_path, device_ip)



if __name__ == "__main__":
    main()
