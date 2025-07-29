import requests
from .command_base import CliCommand
from .utils import error, check_response_code
from tabulate import tabulate


class ContainerCommand(CliCommand):
    @staticmethod
    def help():
        return 'Operations on containers on device'

    def __init__(self, config):
        self._config = config
        self._apps_api_endpoint = f"http://{config['device_address']}/api/apps/v1.0"

    def setup_parser(self, parser):

        command_subparsers = parser.add_subparsers(title='command', metavar='<command>', dest='container_command',
                                                   required=True)

        list_parser = command_subparsers.add_parser('list', aliases=['ls'], help='List all installed containers')
        list_parser.add_argument('container_name', nargs='?', default=None)

        rm_parser = command_subparsers.add_parser('remove', aliases=['rm'], help='Remove an installed container')
        rm_parser.add_argument('container_name', help='The name of the container to be removed')

        logs_parser = command_subparsers.add_parser('logs', help='Show logs of a running container')
        logs_parser.add_argument('container_name', help='The name of the container to show logs for')
        logs_parser.add_argument('-f', '--follow', action='store_true',
                                 help='Live follow the logs from selected container')

        start_parser = command_subparsers.add_parser('start', help='Start an container')
        start_parser.add_argument('container_name', help='The name of the container to start')

        stop_parser = command_subparsers.add_parser('stop', help='Stop an container')
        stop_parser.add_argument('container_name', help='The name of the container to stop')

        restart_parser = command_subparsers.add_parser('restart', help='Restart an container')
        restart_parser.add_argument('container_name', help='The name of the container to restart')

        enable_parser = command_subparsers.add_parser('enable', help='Enable an container')
        enable_parser.add_argument('container_name', help='The name of the container to enable')

        disable_parser = command_subparsers.add_parser('disable', help='Disable an container')
        disable_parser.add_argument('container_name', help='The name of the container to disable')

        status_parser = command_subparsers.add_parser('status', help='Get status from an container')
        status_parser.add_argument('container_name', help='The name of the container to get status from')

    def run(self, args):
        command = args.container_command
        aliases = {
            'ls': 'list',
            'rm': 'remove'
        }

        func = getattr(self, command if command not in aliases else aliases[command])
        if func is None:
            raise RuntimeError(f'Func for command {args.container_command} is not implemented')
        func(args)

    def handle_exception(self, exception):
        try:
            raise exception
        except requests.ConnectionError:
            error(f"Could not connect to device.")

    def list(self, args):
        if args.container_name is not None:
            self._print_containers([self._get_container(args.container_name)])
        else:
            self._print_containers(self._get_containers())

    def remove(self, args):
        data = check_response_code(requests.post(f'{self._apps_api_endpoint}/containers/{args.container_name}/remove',
                                                 cookies=self._config["cookies"],
                                                 headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "removed")

    def logs(self, args):
        data = check_response_code(requests.get(f'{self._apps_api_endpoint}/containers/{args.container_name}/logs',
                                                cookies=self._config["cookies"], headers=self._config["extra_headers"]))
        print(data)
        if data:
            print(data.text)
        else:
            error(f"App {args.container_name} is not installed")

    def start(self, args):
        data = check_response_code(requests.post(f'{self._apps_api_endpoint}/containers/{args.container_name}/start',
                                                 cookies=self._config["cookies"],
                                                 headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "started")

    def stop(self, args):
        data = check_response_code(requests.post(f'{self._apps_api_endpoint}/containers/{args.container_name}/stop',
                                                 cookies=self._config["cookies"],
                                                 headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "stopped")

    def restart(self, args):
        data = check_response_code(requests.post(f'{self._apps_api_endpoint}/containers/{args.container_name}/restart',
                                                 cookies=self._config["cookies"],
                                                 headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "restarted")

    def enable(self, args):
        data = check_response_code(requests.post(f'{self._apps_api_endpoint}/containers/{args.container_name}/enable',
                                                 cookies=self._config["cookies"],
                                                 headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "enabled")

    def disable(self, args):
        data = check_response_code(requests.post(f'{self._apps_api_endpoint}/containers/{args.container_name}/disable',
                                                 cookies=self._config["cookies"],
                                                 headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "disabled")

    def status(self, args):
        data = check_response_code(requests.get(f'{self._apps_api_endpoint}/containers/{args.container_name}/status',
                                                cookies=self._config["cookies"], headers=self._config["extra_headers"]))
        self._print_container_result(data, args.container_name, "status")

    def _get_container(self, container):
        data = check_response_code(
            requests.get(f'{self._apps_api_endpoint}/containers/{container}', cookies=self._config["cookies"],
                         headers=self._config["extra_headers"]))
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
                error(f"App {container} is not installed")

    def _get_containers(self):
        containers = check_response_code(
            requests.get(f'{self._apps_api_endpoint}/containers', cookies=self._config["cookies"],
                         headers=self._config["extra_headers"]))
        if containers:
            return containers.json()
        else:
            error(f"Failed to get containers")

    def _print_containers(self, containers):
        headers = ["Name", "ID", "Image", "Status"]
        matrix = []
        for container in containers:
            matrix.append([container["name"],
                           container["id"],
                           container["image"],
                           container["status"]])
            print(tabulate(matrix, headers=headers))

    def _print_container_result(self, data, container, success_message):
        try:
            body = data.json()
        except:
            body = {}

        if data:
            if "message" in body:
                print(body["message"])
            else:
                print(f'App {container} {success_message}')
        else:
            if "message" in body:
                error(body["message"])
            else:
                error(f"App {container} is not installed")
