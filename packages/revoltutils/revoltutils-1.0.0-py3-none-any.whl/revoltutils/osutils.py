import os
import platform
import socket
import time
import getpass
from typing import Optional


class OSUtils:
    @staticmethod
    def is_linux() -> bool:
        return platform.system().lower() == "linux"

    @staticmethod
    def is_windows() -> bool:
        return platform.system().lower() == "windows"

    @staticmethod
    def is_macos() -> bool:
        return platform.system().lower() == "darwin"

    @staticmethod
    def os_name() -> str:
        return platform.system()

    @staticmethod
    def os_version() -> str:
        return platform.version()

    @staticmethod
    def platform_info() -> str:
        return platform.platform()

    @staticmethod
    def architecture() -> str:
        return platform.machine()

    @staticmethod
    def hostname() -> str:
        return socket.gethostname()

    @staticmethod
    def uptime_seconds() -> Optional[float]:
        if OSUtils.is_linux():
            try:
                with open('/proc/uptime', 'r') as f:
                    return float(f.readline().split()[0])
            except Exception:
                return None
        elif OSUtils.is_macos():
            try:
                import subprocess
                output = subprocess.check_output(['sysctl', '-n', 'kern.boottime']).decode()
                boot_time = int(output.split('=')[1].split(',')[0].strip())
                return time.time() - boot_time
            except Exception:
                return None
        else:
            return None  # Not implemented for Windows yet

    @staticmethod
    def env(key: str, default: Optional[str] = None) -> Optional[str]:
        return os.environ.get(key, default)

    @staticmethod
    def set_env(key: str, value: str) -> None:
        os.environ[key] = value

    @staticmethod
    def current_process_id() -> int:
        return os.getpid()

    @staticmethod
    def parent_process_id() -> int:
        return os.getppid()

    @staticmethod
    def current_user() -> str:
        return getpass.getuser()

    @staticmethod
    def cwd() -> str:
        return os.getcwd()

    @staticmethod
    def change_dir(path: str) -> None:
        os.chdir(path)
