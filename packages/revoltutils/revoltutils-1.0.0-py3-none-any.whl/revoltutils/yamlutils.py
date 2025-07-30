import aiofiles
import yaml
from typing import Any, Dict, List, Optional, Tuple

class YamlUtils:
    @staticmethod
    async def read_yaml(path: str) -> Dict[str, Any]:
        async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
            content = await f.read()
            return yaml.safe_load(content) or {}

    @staticmethod
    async def write_yaml(path: str, data: Dict[str, Any], overwrite: bool = True) -> None:
        if not overwrite:
            existing_data = await YamlUtils.read_yaml(path)
            existing_data.update(data)
            data = existing_data
        async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
            dumped = yaml.safe_dump(data, default_flow_style=False)
            await f.write(dumped)

    @staticmethod
    async def get_value(path: str, key: str) -> Any:
        data = await YamlUtils.read_yaml(path)
        return data.get(key)

    @staticmethod
    async def set_value(path: str, key: str, value: Any) -> None:
        data = await YamlUtils.read_yaml(path)
        data[key] = value
        await YamlUtils.write_yaml(path, data)

    @staticmethod
    async def delete_key(path: str, key: str) -> bool:
        data = await YamlUtils.read_yaml(path)
        if key in data:
            del data[key]
            await YamlUtils.write_yaml(path, data)
            return True
        return False

    @staticmethod
    async def get_all_keys(path: str) -> List[str]:
        data = await YamlUtils.read_yaml(path)
        return list(data.keys())

    @staticmethod
    async def custom_key_value(path: str) -> Dict[str, List[str]]:
        data = await YamlUtils.read_yaml(path)
        result = {}
        for key, value in data.items():
            if isinstance(value, list):
                result[key] = [str(v) for v in value]
        return result

    @staticmethod
    async def dual_key_value(path: str, separator: str = ":") -> List[Tuple[str, str, str]]:
        data = await YamlUtils.read_yaml(path)
        result = []
        for key, values in data.items():
            if isinstance(values, list):
                for entry in values:
                    if separator in entry:
                        secret, name = entry.split(separator, 1)
                        result.append((key, secret.strip(), name.strip()))
        return result

    @staticmethod
    async def get_nested(path: str, keys: List[str]) -> Optional[Any]:
        data = await YamlUtils.read_yaml(path)
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return None
        return data