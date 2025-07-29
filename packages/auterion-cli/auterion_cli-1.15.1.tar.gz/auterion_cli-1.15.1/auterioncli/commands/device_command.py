import requests
import zeroconf
import time
import socket
from .command_base import CliCommand
from tabulate import tabulate
from .utils import error, eprint, check_response_code
from getpass import getpass
from auterioncli.meta_util import get_device_presence

def _find_devices_zeroconf(timeout):
    devices = {}

    class Listener(zeroconf.ServiceListener):
        def add_service(self, zc_inst, service_type, name):
            if name.startswith('Auterion Skynode API'):
                info = zc.get_service_info(service_type, name)
                if b'serial' in info.properties and b'aos-version' in info.properties:
                    serial = info.properties[b'serial'].decode()
                    version = info.properties[b'aos-version'].decode()
                    addresses = {socket.inet_ntoa(a) for a in info.addresses}

                    if serial in devices:
                        devices[serial]['addresses'].update(addresses)
                    else:
                        devices[serial] = {
                            'version': version,
                            'addresses': addresses
                        }

        def remove_service(self, zc_inst, service_type, name):
            pass

        def update_service(self, zc_inst, service_type, name):
            pass
    try:
        zc = zeroconf.Zeroconf()
        listener = Listener()
        browser = zeroconf.ServiceBrowser(zc, '_https._tcp.local.', listener)
        time.sleep(timeout)
        zc.close()
    except OSError as e:
        eprint('Warn: Zeroconf initialization failed: %s' % e)
        eprint('      Dynamic discovery will not be available.')

    return devices


def _find_devices_address(addresses, timeout=0.5):
    devices = {}
    for address in addresses:
        url = f"http://{address}/api/sysinfo/v1.0/device"
        try:
            response = requests.get(url, timeout=timeout)
            if response:
                data = response.json()
                if 'uuid' in data:
                    serial = data['uuid']
                    if serial in devices:
                        devices[serial]['addresses'].add(address)
                    else:
                        devices[serial] = {
                            'version': data['auterion_os'] if 'auterion_os' in data else None,
                            'addresses': {address}
                        }

        except:
            pass
    return devices


def _find_devices(candidates, timeout=0.5):
    devices = {}
    devices.update(_find_devices_address(candidates, timeout))
    devices.update(_find_devices_zeroconf(1))
    return devices


def _get_default_candidates():
    return ['127.0.0.1', '10.41.1.1', '10.41.2.1', '10.41.200.2']


class DeviceCommand(CliCommand):
    @staticmethod
    def help():
        return 'Discover and select Auterion device to work with'

    def needs_device(self, args):
        return False

    def __init__(self, config):
        self._config = config

    def setup_parser(self, parser):
        command_subparsers = parser.add_subparsers(title='command', metavar='<command>', dest='device_command',
                                                   required=True)
        discover_parser = command_subparsers.add_parser('discover', help='Discover reachable Auterion devices')
        select_parser = command_subparsers.add_parser('select', help='Select a specific Auterion device to work with')
        select_parser.add_argument('serial', nargs='?', help='Serial number of device to connect')
        select_parser.add_argument('--ip', help='Use this IP to connect to the specified device')

        deselect_parser = command_subparsers.add_parser('deselect', help='Unselect currently specified device')

        login_parser = command_subparsers.add_parser('login', help='Login to the selected device')
        login_parser.add_argument('--password', '-p', help='Password to use for login')

        logout_parser = command_subparsers.add_parser('logout', help='Logout from the selected device')

    def run(self, args):

        command = args.device_command
        func = getattr(self, command)
        if func is None:
            raise RuntimeError(f'Func for command {args.app_command} is not implemented')
        func(args)

    def discover(self, args):
        selected_serial = self._config["persistent"]["selected_serial"]
        selected_address = self._config["persistent"]["selected_address"]
        devices = _find_devices(_get_default_candidates())
        print('')
        print('Found devices')
        devices_list = [{
            'selected': '*' if serial == selected_serial and selected_address in rest['addresses'] else ' ',
            'serial': serial,
            **rest
        } for serial, rest in devices.items()]
        print(tabulate(devices_list, headers='keys'))
        print('')
        print('Note: Use \'device select\' command to select a device to interact with')
        print('      Use \'device deselect\' command to reset selection')

    def select(self, args):
        if args.serial is None and args.ip is None:
            error(f"Must specify either an IP or a serial for the device.")
        devices = _find_devices([args.ip] if args.ip else _get_default_candidates(), 12)
        serial = args.serial

        if serial is not None:
            if serial not in devices:
                error(f"Device with serial {serial} not reachable. \n"
                    f"Use \'device discover\' command to find reachable devices.")
            if args.ip is not None and args.ip not in devices[serial]['addresses']:
                error(f"Device with serial {serial} reachable, but not on {args.ip}. \n"
                    f"Use \'device discover\' command to find reachable devices.")
            address = next(iter(devices[serial]['addresses']))
        else:
            address = args.ip
            for k,v in devices.items():
                if address in v['addresses']:
                    serial = k
                    break
            if serial is None:
                error(f"Device at IP {address} not reachable. \n"
                    f"Use \'device discover\' command to find reachable devices.")

        # clear cookies from previous device
        self._config["persistent"]["cookies"] = None
        self._config["persistent"]["selected_serial"] = serial
        self._config["persistent"]["selected_address"] = address

        print(f"Selected device with ID {serial} on address {address}")

    def deselect(self, args):
        selected_serial = self._config["persistent"]["selected_serial"]
        selected_address = self._config["persistent"]["selected_address"]
        self._config["persistent"]["selected_serial"] = None
        self._config["persistent"]["selected_address"] = None
        self._config["persistent"]["cookies"] = None

        if selected_serial is None and selected_address is None:
            print('No vehicle was selected.')
        else:
            print(f'Deselected vehicle {selected_serial} on {selected_address}.\nNo device selected now.')

    def login(self, args):
        if args.password is not None:
            password = args.password
        else:
            password = getpass("Password: ")

        url = f"http://{self._config['persistent']['selected_address']}/api/sysinfo/v1.0/login"
        response = check_response_code(requests.post(url, json={"password": password}))
        # check_response_code has exited already if there was an error

        # extract cookies
        self._config["persistent"]["cookies"] = dict(response.cookies)
        print("Logged in successfully.")

    def logout(self, args):
        del self._config["persistent"]["cookies"]
        print("Removed login information.")
