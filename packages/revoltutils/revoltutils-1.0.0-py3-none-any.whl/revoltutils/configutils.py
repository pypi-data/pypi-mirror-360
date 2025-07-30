import aiofiles
import yaml
from pathlib import Path
from appdirs import user_config_dir
from typing import Optional, List

class Config:
    def __init__(self, app_name: str = "App"):
        if not app_name:
            raise ValueError("App name is required")
        self.app_name = app_name
        self._config_dir = Path(user_config_dir(app_name))
        self._config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self._config_dir

    def get_config_path(self, filename: str = "provider-config.yaml") -> Path:
        """Get the full path of a given config file name."""
        return self._config_dir / filename

    def config_exists(self, filename: str = "provider-config.yaml") -> bool:
        """Check if the given config file exists."""
        return self.get_config_path(filename).exists()

    async def create_config_file(
        self,
        filename: str = "provider-config.yaml",
        content: Optional[dict] = None,
        overwrite: bool = False
    ) -> Path:
        """
        Create a YAML config file asynchronously.

        Args:
            filename: File to create.
            content: YAML-serializable dict.
            overwrite: Whether to overwrite if file exists.
        """
        path = self.get_config_path(filename)
        if path.exists() and not overwrite:
            return path

        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            dumped = yaml.safe_dump(content or {}, default_flow_style=False)
            await f.write(dumped)
        return path

    async def read_config(self, filename: str = "provider-config.yaml") -> dict:
        """Read a YAML config file asynchronously."""
        path = self.get_config_path(filename)
        if not path.exists():
            return {}

        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return yaml.safe_load(content) or {}

    async def write_config(
        self,
        data: dict,
        filename: str = "provider-config.yaml",
        overwrite: bool = True
    ) -> Path:
        """Write a YAML file asynchronously."""
        return await self.create_config_file(filename, content=data, overwrite=overwrite)

    def list_configs(self) -> List[Path]:
        """List all `.yaml` config files."""
        return list(self._config_dir.glob("*.yaml"))

    def delete_config(self, filename: str) -> bool:
        """Delete a config file."""
        path = self.get_config_path(filename)
        if path.exists():
            path.unlink()
            return True
        return False

    async def ensure_config(
        self,
        filename: str = "provider-config.yaml",
        default_content: Optional[dict] = None
    ) -> Path:
        """Ensure a config file exists, create it with default content if missing."""
        if not self.config_exists(filename):
            return await self.create_config_file(filename, content=default_content or {})
        return self.get_config_path(filename)