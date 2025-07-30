import os
import sys
import aiofiles
import json
from typing import Any, AsyncGenerator


class FileUtils:
    @staticmethod
    async def file_exist(filepath: str) -> bool:
        return os.path.isfile(filepath)

    @staticmethod
    async def file_exist_in(filepath: str, directory: str) -> bool:
        full_path = os.path.join(directory, filepath)
        return await FileUtils.file_exist(full_path)

    @staticmethod
    async def read(filepath: str) -> str:
        async with aiofiles.open(filepath, mode='r') as f:
            return await f.read()

    @staticmethod
    async def readlines(filepath: str) -> list[str]:
        async with aiofiles.open(filepath, mode='r') as f:
            return await f.readlines()

    @staticmethod
    async def stream(filepath: str) -> AsyncGenerator[str, None]:
        async with aiofiles.open(filepath, mode='r') as f:
            async for line in f:
                yield line.rstrip('\n')

    @staticmethod
    async def read_with_buffer(filepath: str, buffer_size: int = 1024) -> AsyncGenerator[str, None]:
        async with aiofiles.open(filepath, mode='r') as f:
            while True:
                chunk = await f.read(buffer_size)
                if not chunk:
                    break
                yield chunk

    @staticmethod
    async def copy_file(src: str, dst: str) -> None:
        async with aiofiles.open(src, mode='rb') as f_src:
            async with aiofiles.open(dst, mode='wb') as f_dst:
                while True:
                    chunk = await f_src.read(4096)
                    if not chunk:
                        break
                    await f_dst.write(chunk)

    @staticmethod
    async def readable(filepath: str) -> bool:
        return os.access(filepath, os.R_OK)

    @staticmethod
    async def writeable(filepath: str) -> bool:
        return os.access(filepath, os.W_OK)

    @staticmethod
    async def has_permission(filepath: str, mode: str = 'a') -> bool:
        try:
            async with aiofiles.open(filepath, mode=mode):
                return True
        except (PermissionError, OSError):
            return False

    @staticmethod
    async def is_empty(filepath: str) -> bool:
        return os.path.exists(filepath) and os.stat(filepath).st_size == 0

    @staticmethod
    def is_stdin() -> bool:
        return not sys.stdin.isatty()


    @staticmethod
    async def write(filepath: str, content: str, mode: str = 'w') -> None:
        async with aiofiles.open(filepath, mode=mode) as f:
            await f.write(content)

    @staticmethod
    async def json_write(filepath: str, data: Any, mode: str = 'w', indent: int = 2) -> None:
        async with aiofiles.open(filepath, mode=mode) as f:
            json_str = json.dumps(data, indent=indent)
            await f.write(json_str)

    @staticmethod
    async def create_file(filepath: str) -> None:
        async with aiofiles.open(filepath, mode='a') as f:
            pass  # creates the file if it doesn't exist

    @staticmethod
    async def delete_file(filepath: str) -> bool:
        try:
            os.remove(filepath)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
