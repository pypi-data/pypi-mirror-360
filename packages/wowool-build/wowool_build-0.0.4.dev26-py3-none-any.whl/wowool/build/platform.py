import platform
import sys
from typing import Optional


def _get_machine_name() -> Optional[str]:
    """
    Returns the machine architecture name in Docker-compatible format
    """
    machine = platform.machine().lower()

    # Map from system architecture names to Docker platform names
    docker_arch_map = {
        # "x86_64": "amd64",
        # "amd64": "amd64",
        # "i386": "386",
        # "i686": "386",
        # "aarch64": "arm64",
        # "arm64": "arm64",
        # "armv7l": "arm/v7",
        # "armv6l": "arm/v6",
        # "s390x": "s390x",
        # "ppc64le": "ppc64le",
        # "ppc64": "ppc64",
    }

    return docker_arch_map.get(machine, machine)


def _get_system_name() -> Optional[str]:
    platform_name = platform.system()
    if "Linux" == platform_name:
        return f"{platform.system()}-{_get_machine_name()}-{platform.libc_ver()[0]}"
    elif "Darwin" == platform_name:
        return f"{platform.system()}-{_get_machine_name()}"
    elif "Windows" == platform_name:
        return f"{platform.system()}-{_get_machine_name()}-{platform.win32_ver()[0]}"


def _get_architecture_name() -> Optional[str]:
    platform_name = platform.system()
    if "Linux" == platform_name:
        return f"{_get_machine_name()}-{platform.libc_ver()[0]}"
    elif "Darwin" == platform_name:
        return _get_machine_name()
    elif "Windows" == platform_name:
        return f"{_get_machine_name()}-{platform.win32_ver()[0]}"


def _get_os_name():
    platforms = {
        "linux1": "linux",
        "linux2": "linux",
        "darwin": "macos",
        "win32": "windows",
    }
    return platforms[sys.platform] if sys.platform in platforms else sys.platform


SYSTEM_NAME = _get_system_name()
OS_NAME = _get_os_name()
IS_PTY = sys.stdout.isatty() if OS_NAME != "windows" else False
IS_POSIX = OS_NAME != "win32"
ARCHITECTURE_NAME = _get_architecture_name()
