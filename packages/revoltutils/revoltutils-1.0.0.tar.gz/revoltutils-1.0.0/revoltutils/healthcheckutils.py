import asyncio
from typing import Optional
from dataclasses import dataclass


@dataclass
class ConnectionInfo:
    host: str
    port: int
    protocol: str
    successful: bool
    message: str
    error: Optional[Exception] = None


class HealthCheck:
    @staticmethod
    async def check_connection(host: str, port: int, timeout: float = 10.0) -> ConnectionInfo:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return ConnectionInfo(
                host=host,
                port=port,
                protocol="tcp",
                successful=True,
                message=f"TCP Connect ({host}:{port}): Successful"
            )
        except Exception as e:
            return ConnectionInfo(
                host=host,
                port=port,
                protocol="tcp",
                successful=False,
                message=f"TCP Connect ({host}:{port}): Failed",
                error=e
            )
