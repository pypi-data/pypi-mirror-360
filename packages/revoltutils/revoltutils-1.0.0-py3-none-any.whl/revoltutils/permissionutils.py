import os
import getpass
import pwd
import grp
from typing import Optional


class PermissionUtils:
    @staticmethod
    def is_root() -> bool:
        return os.geteuid() == 0

    @staticmethod
    def current_user() -> str:
        return getpass.getuser()

    @staticmethod
    def user_id() -> int:
        return os.getuid()

    @staticmethod
    def group_id() -> int:
        return os.getgid()

    @staticmethod
    def user_home(username: Optional[str] = None) -> str:
        if username:
            return pwd.getpwnam(username).pw_dir
        return os.path.expanduser("~")

    @staticmethod
    def file_owner(filepath: str) -> str:
        stat_info = os.stat(filepath)
        return pwd.getpwuid(stat_info.st_uid).pw_name

    @staticmethod
    def file_group(filepath: str) -> str:
        stat_info = os.stat(filepath)
        return grp.getgrgid(stat_info.st_gid).gr_name

    @staticmethod
    def is_readable(path: str) -> bool:
        return os.access(path, os.R_OK)

    @staticmethod
    def is_writable(path: str) -> bool:
        return os.access(path, os.W_OK)

    @staticmethod
    def is_executable(path: str) -> bool:
        return os.access(path, os.X_OK)

    @staticmethod
    def has_all_permissions(path: str) -> bool:
        return os.access(path, os.R_OK | os.W_OK | os.X_OK)

    @staticmethod
    def chmod(path: str, mode: int) -> bool:
        try:
            os.chmod(path, mode)
            return True
        except Exception:
            return False

    @staticmethod
    def chown(path: str, user: str, group: Optional[str] = None) -> bool:
        try:
            uid = pwd.getpwnam(user).pw_uid
            gid = grp.getgrnam(group).gr_gid if group else -1
            os.chown(path, uid, gid)
            return True
        except Exception:
            return False
