import os
import sys
import platform
import time
import socket
import shutil
import getpass
import psutil
from datetime import datetime, timezone, timedelta
from typing import Optional, List


class SystemUtils:
    """
    Utility class for system-level information and introspection.
    """

    @staticmethod
    def os_name() -> str:
        return platform.system()

    @staticmethod
    def os_version() -> str:
        return platform.version()

    @staticmethod
    def os_release() -> str:
        return platform.release()

    @staticmethod
    def architecture() -> str:
        return platform.machine()

    @staticmethod
    def python_version() -> str:
        return platform.python_version()

    @staticmethod
    def cpu_count(logical: bool = True) -> int:
        return os.cpu_count() if logical else psutil.cpu_count(logical=False)

    @staticmethod
    def memory_info() -> dict:
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        }

    @staticmethod
    def disk_usage(path: str = "/") -> dict:
        usage = shutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": round((usage.used / usage.total) * 100, 2)
        }

    @staticmethod
    def hostname() -> str:
        return socket.gethostname()

    @staticmethod
    def current_user() -> str:
        return getpass.getuser()

    @staticmethod
    def uptime_seconds() -> float:
        return time.time() - psutil.boot_time()

    @staticmethod
    def uptime_human() -> str:
        seconds = int(SystemUtils.uptime_seconds())
        return str(timedelta(seconds=seconds))

    @staticmethod
    def is_linux() -> bool:
        return sys.platform.startswith("linux")

    @staticmethod
    def is_windows() -> bool:
        return sys.platform.startswith("win")

    @staticmethod
    def is_macos() -> bool:
        return sys.platform.startswith("darwin")

    @staticmethod
    def timezone_name() -> str:
        return time.tzname[0]

    @staticmethod
    def local_datetime() -> datetime:
        return datetime.now()

    @staticmethod
    def utc_datetime() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def is_reboot_required() -> bool:
        """
        Check if system reboot is required (Linux specific).
        """
        return os.path.exists("/var/run/reboot-required")

    @staticmethod
    def load_average() -> Optional[tuple]:
        """
        Get system load average (Unix only).
        """
        if hasattr(os, "getloadavg"):
            return os.getloadavg()
        return None

    @staticmethod
    def running_processes() -> List[str]:
        """
        List all running process names.
        """
        return [p.name() for p in psutil.process_iter()]

    @staticmethod
    def is_process_running(name: str) -> bool:
        """
        Check if a process is running by name.
        """
        return any(name.lower() in p.name().lower() for p in psutil.process_iter())

    @staticmethod
    def supports_color() -> bool:
        """
        Checks if the terminal supports color.
        """
        return sys.stdout.isatty()

    @staticmethod
    def is_64bit() -> bool:
        return sys.maxsize > 2**32
