import requests
from .command_base import CliCommand
from .utils import error

class InfoCommand(CliCommand):
    @staticmethod
    def help():
        return 'Information about your Auterion device'

    def __init__(self, config):
        self._sysinfo_api_endpoint = f"http://{config['device_address']}/api/sysinfo/v1.0"

    def setup_parser(self, parser):
        pass

    def handle_exception(self, exception):
        try:
            raise exception
        except requests.ConnectionError:
            error(f"Could not connect to device.")

    def run(self, args):
        print("===== Device Information =====")
        device = self._get_information("device")
        if device:
            print("UUID: {}".format(device['uuid']))
            print("FCID: {}".format(device['fcid']))
            print("Release: {}".format(device['release']))
            print("AuterionOS: {}".format(device['auterion_os']))
            if "px4" in device:
                print("PX4: {}".format(device['px4']))
            print("AOS hash: {}".format(device['hash']))
            if "px4_hash" in device:
                print("PX4 hash: {}".format(device['px4_hash']))
        else:
            print("No device information available")

        print("\n===== FC Information =====")
        fc = self._get_information("fc")
        if fc:
            print("Target: {}".format(fc['target']))
            if "px4" in device:
                print("PX4: {}".format(fc['px4']))
            if "px4_hash" in device:
                print("PX4: {}".format(fc['px4_hash']))
            print("Expected PX4: {}".format(fc['expected_px4_version']))
            print("Expected hash: {}".format(fc['expected_px4_hash']))
            print("Found FMU binary: {}".format(fc['fmu_binary']))
            print("Found FMU package: {}".format(fc['fmu_package']))
            print("Found FMU dev binary: {}".format(fc['fmu_dev_package']))

        else:
            print("No FC information available")

        print("\n===== Connectivity Information =====")
        connectivity = self._get_information("connectivity")
        if connectivity:
            print(f"Connectivity: {connectivity['status']}")
        else:
            print("No connectivity information available")

        print("\n===== Hardware Information =====")
        hardware = self._get_information("hardware")
        if hardware:
            for name, state in hardware.items():
                state_str = "[\033[32mGOOD\033[39m]" if state else "[\033[31mERROR\033[39m]"
                print("{}: {}".format(name.replace("_", " "), state_str))
        else:
            print("No hardware information available")

        print("\n===== Network Information =====")
        network = self._get_information("network")
        if network:
            for interface, data in network.items():
                print("{}:".format(interface))
                for k, v in data.items():
                    print("\t{}:{}".format(k, v))
        else:
            print("No network information available")

        print("\n===== Software Information =====")
        software = self._get_information("software")
        if software:
            for name, data in software.items():
                print("{}:".format(name))
                if data['status'] == "running":
                    status_str = "[\033[32mRUNNING\033[39m]"
                elif data['status'] == "succeeded":
                    status_str = "[\033[32mSUCCEEDED\033[39m]"
                else:
                    status_str = "[\033[31mERROR\033[39m]"
                print("\tversion: {}".format(data.get('version', data.get('hash', 'no version information'))))
                print("\tstatus: {}".format(status_str))
        else:
            print("No software information available")

        print("\n===== System services Information =====")
        services = self._get_information("services")
        if services:
            for software, data in services.items():
                print("{}:".format(software))
                if data['status'] == "running":
                    status_str = "[\033[32mRUNNING\033[39m]"
                elif data['status'] == "succeeded":
                    status_str = "[\033[32mSUCCEEDED\033[39m]"
                else:
                    status_str = "[\033[31mERROR\033[39m]"
                print("\tstatus: {}".format(status_str))
        else:
            print("No services information available")

        print("\n===== USB devices Information =====")
        devices = self._get_information("usb_devices")
        if devices:
            for data in devices["usb_devices"]:
                if "product" in data:
                    print(f"Product: {data['product']}")
                if "serial_number" in data:
                    print(f"Serial number: {data['serial_number']}")
                if "manufacturer" in data:
                    print(f"Manufacturer: {data['manufacturer']}")
                print("")
        else:
            print("No USB devices information available")

        print("\n===== Partitions Information =====")
        partitions = self._get_information("partitions")
        if partitions:
            for data in partitions["partitions"]:
                if "partition" in data:
                    print(f"Partition: {data['partition']}")
                if "mount" in data:
                    print(f"Mount point: {data['mount']}")
                if "size" in data:
                    print(f"Size: {data['size']}")
                if "used" in data:
                    print(f"Used: {data['used']}")
                if "available" in data:
                    print(f"Available: {data['available']}")
                if "use" in data:
                    print(f"Use: {data['use']}")
                print("")
        else:
            print("No partitions information available")

    def _get_information(self, target):
        try:
            response = requests.get(f"{self._sysinfo_api_endpoint}/{target}", timeout=5)
            if response:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Failed to get {target} information:")
            print(e)
            return None
