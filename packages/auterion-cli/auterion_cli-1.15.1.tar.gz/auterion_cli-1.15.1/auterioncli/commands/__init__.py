from .app_command import AppCommand
from .container_command import ContainerCommand
from .info_command import InfoCommand
from .report_command import ReportCommand
from .device_command import DeviceCommand


def available_commands(config):
    return {
        'app': AppCommand(config),
        'container': ContainerCommand(config),
        'info': InfoCommand(config),
        'report': ReportCommand(config),
        'device': DeviceCommand(config)
    }
