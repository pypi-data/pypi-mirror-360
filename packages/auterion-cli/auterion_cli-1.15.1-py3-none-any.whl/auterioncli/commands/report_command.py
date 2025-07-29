import requests
from .command_base import CliCommand
from .utils import download_file, error


class ReportCommand(CliCommand):
    @staticmethod
    def help():
        return 'Download a diagnostic report from your Auterion device'

    def __init__(self, config):
        self._config = config
        self._sysinfo_api_endpoint = f"http://{config['device_address']}/api/sysinfo/v1.0"

    def setup_parser(self, parser):
        parser.add_argument('-o', '--output', help='output path of the diagnostic report', default='report.zip')

    def run(self, args):
        report_name = args.output
        if not report_name.endswith(".zip"):
            report_name += ".zip"
        print("Generating report... This may take a few minutes")
        print(f"Report will be downloaded to {report_name}")
        download_file(f"{self._sysinfo_api_endpoint}/report", report_name, self._config['cookies'],
                      self._config['extra_headers'])

    def handle_exception(self, exception):
        try:
            raise exception
        except requests.ConnectionError:
            error(f"Could not connect to device.")
