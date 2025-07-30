import socket
import ipaddress
import asyncio
import httpx
import aiodns
from typing import List, Optional


class IPUtils:
    IPV4_INTERNAL = [
        "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8", "169.254.0.0/16",
        "172.16.0.0/12", "192.0.0.0/24", "192.0.2.0/24", "192.88.99.0/24", "192.168.0.0/16",
        "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24", "224.0.0.0/4", "240.0.0.0/4"
    ]

    IPV6_INTERNAL = [
        "::1/128", "64:ff9b::/96", "100::/64", "2001::/32", "2001:10::/28", "2001:20::/28",
        "2001:db8::/32", "2002::/16", "fc00::/7", "fe80::/10", "ff00::/8"
    ]

    def __init__(self):
        self.resolver = aiodns.DNSResolver()

    def is_ip(self, value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    def is_ipv4(self, value: str) -> bool:
        try:
            return isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address)
        except ValueError:
            return False

    def is_ipv6(self, value: str) -> bool:
        try:
            return isinstance(ipaddress.ip_address(value), ipaddress.IPv6Address)
        except ValueError:
            return False

    def is_asn(self, value: str) -> bool:
        if value.upper().startswith("AS"):
            value = value[2:]
        return value.isdigit()

    def is_internal(self, ip: str) -> bool:
        try:
            ip_obj = ipaddress.ip_address(ip)
            ranges = self.IPV4_INTERNAL if isinstance(ip_obj, ipaddress.IPv4Address) else self.IPV6_INTERNAL
            return any(ip_obj in ipaddress.ip_network(cidr) for cidr in ranges)
        except ValueError:
            return False

    def is_port(self, value: str) -> bool:
        try:
            port = int(value)
            return 0 < port < 65536
        except ValueError:
            return False

    def is_cidr(self, value: str) -> bool:
        try:
            ipaddress.ip_network(value, strict=False)
            return True
        except ValueError:
            return False

    def to_cidr(self, ip: str) -> Optional[ipaddress._BaseNetwork]:
        if self.is_ipv4(ip):
            ip += "/32"
        elif self.is_ipv6(ip):
            ip += "/128"
        try:
            return ipaddress.ip_network(ip, strict=False)
        except ValueError:
            return None

    def as_ipv4_cidr(self, ip: str) -> str:
        return ip + "/32" if self.is_ipv4(ip) else ip

    def as_ipv6_cidr(self, ip: str) -> str:
        return ip + "/64" if self.is_ipv6(ip) else ip

    async def whats_my_ip(self, timeout: int = 2) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get("https://checkip.amazonaws.com")
                return resp.text.strip()
        except httpx.RequestError:
            return None

    async def get_source_ip(self, target: str = "8.8.8.8") -> Optional[str]:
        try:
            def _connect():
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((target, 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            return await asyncio.to_thread(_connect)
        except Exception:
            return None

    async def to_fqdn(self, ip: str) -> List[str]:
        try:
            result = await self.resolver.gethostbyaddr(ip)
            return [result.name]
        except aiodns.error.DNSError:
            return []

