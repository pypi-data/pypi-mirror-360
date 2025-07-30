import os
import shutil
from typing import List

class FolderUtils:
    @staticmethod
    async def folder_exists(path: str) -> bool:
        return os.path.isdir(path)

    @staticmethod
    async def create_folder(path: str, exist_ok: bool = True) -> None:
        os.makedirs(path, exist_ok=exist_ok)

    @staticmethod
    async def delete_folder(path: str) -> bool:
        try:
            shutil.rmtree(path)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    @staticmethod
    async def list_dirs(path: str) -> List[str]:
        return [entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]

    @staticmethod
    async def list_files(path: str) -> List[str]:
        return [entry for entry in os.listdir(path) if os.path.isfile(os.path.join(path, entry))]

    @staticmethod
    async def list_all(path: str) -> List[str]:
        return os.listdir(path)

    @staticmethod
    async def is_empty(path: str) -> bool:
        if not os.path.isdir(path):
            return False
        return len(os.listdir(path)) == 0

    @staticmethod
    async def rename_folder(old_path: str, new_path: str) -> bool:
        try:
            os.rename(old_path, new_path)
            return True
        except Exception:
            return False

    @staticmethod
    async def copy_folder(src: str, dst: str) -> bool:
        try:
            shutil.copytree(src, dst)
            return True
        except FileExistsError:
            return False  # destination already exists
        except Exception:
            return False

    @staticmethod
    async def folder_writable(path: str) -> bool:
        return os.access(path, os.W_OK)

    @staticmethod
    async def folder_readable(path: str) -> bool:
        return os.access(path, os.R_OK)

    @staticmethod
    async def has_permission(path: str) -> bool:
        return os.access(path, os.R_OK | os.W_OK | os.X_OK)
