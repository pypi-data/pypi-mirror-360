import asyncio
import aiodns
import socket
from urllib.parse import urlparse
from typing import List, Optional


class DnsUtils:
    _resolver: Optional[aiodns.DNSResolver] = None
    _nameservers = ["1.1.1.1", "8.8.8.8"]

    @classmethod
    async def init(cls, nameservers: Optional[List[str]] = None):
        if cls._resolver is None:
            loop = asyncio.get_event_loop()
            cls._resolver = aiodns.DNSResolver(
                loop=loop,
                nameservers=nameservers or cls._nameservers,
                rotate=True,
                timeout=3,
                tries=2
            )

    @staticmethod
    def get_domain(url: str) -> str:
        try:
            parsed_url = urlparse(url)
            return parsed_url.hostname or ""
        except Exception:
            return url

    @classmethod
    async def gethostbyname(cls, domain: str) -> List[str]:
        """
        Perform DNS resolution like gethostbyname (returns list of IPs).
        """
        if cls._resolver is None:
            raise RuntimeError("DnsUtils not initialized. Call await DnsUtils.init() first.")

        try:
            result = await cls._resolver.gethostbyname(domain, socket.AF_INET)
            return result.addresses if result and result.addresses else []
        except Exception:
            return []

    @classmethod
    async def resolve(cls, domain: str, qtype: str) -> List[str]:
        if cls._resolver is None:
            raise RuntimeError("DnsUtils not initialized. Call await DnsUtils.init() first.")

        try:
            result = await cls._resolver.query(domain, qtype)
            await asyncio.sleep(0)

            if qtype == "A":
                return [r.host for r in result]
            elif qtype == "AAAA":
                return [r.host for r in result]
            elif qtype == "MX":
                return [r.host for r in result]
            elif qtype == "NS":
                return [r.host for r in result]
            elif qtype == "TXT":
                return [r.text for r in result if hasattr(r, "text")]
            elif qtype == "CNAME":
                return [result.cname] if hasattr(result, "cname") else []
        except Exception:
            return []

        return []

    @classmethod
    async def resolve_a(cls, domain: str) -> List[str]:
        return await cls.resolve(domain, "A")

    @classmethod
    async def resolve_aaaa(cls, domain: str) -> List[str]:
        return await cls.resolve(domain, "AAAA")

    @classmethod
    async def resolve_mx(cls, domain: str) -> List[str]:
        return await cls.resolve(domain, "MX")

    @classmethod
    async def resolve_ns(cls, domain: str) -> List[str]:
        return await cls.resolve(domain, "NS")

    @classmethod
    async def resolve_txt(cls, domain: str) -> List[str]:
        return await cls.resolve(domain, "TXT")

    @classmethod
    async def resolve_cname(cls, domain: str) -> Optional[str]:
        cname_list = await cls.resolve(domain, "CNAME")
        return cname_list[0] if cname_list else None

    @classmethod
    async def get_all_records(cls, domain: str) -> dict:
        domain = cls.get_domain(domain)
        results = await asyncio.gather(
            cls.resolve_a(domain),
            cls.resolve_aaaa(domain),
            cls.resolve_mx(domain),
            cls.resolve_ns(domain),
            cls.resolve_txt(domain),
            cls.resolve_cname(domain),
            return_exceptions=True
        )

        return {
            "A": results[0] if isinstance(results[0], list) else [],
            "AAAA": results[1] if isinstance(results[1], list) else [],
            "MX": results[2] if isinstance(results[2], list) else [],
            "NS": results[3] if isinstance(results[3], list) else [],
            "TXT": results[4] if isinstance(results[4], list) else [],
            "CNAME": results[5] if isinstance(results[5], str) else None,
        }

    @classmethod
    async def is_resolvable(cls, domain: str) -> bool:
        return bool(await cls.resolve_a(domain))

    @classmethod
    async def reverse_lookup(cls, ip: str) -> List[str]:
        try:
            result = await asyncio.to_thread(socket.gethostbyaddr, ip)
            return [result[0]]
        except Exception:
            return []
