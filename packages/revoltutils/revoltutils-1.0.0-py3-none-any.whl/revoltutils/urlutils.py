from urllib.parse import urlparse, urlunparse,urlencode, parse_qs
from typing import List, Optional, Tuple
import tldextract

class UrlUtils:

    @staticmethod
    def ensure_scheme(url: str, default_scheme: str = "https") -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            return f"{default_scheme}://{url}"
        return url

    @staticmethod
    def add_ports(url: str, ports: Optional[List[int]] = None) -> List[str]:
        if not ports:
            return [url]

        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname is None:
            return []

        result_urls = []
        for port in ports:
            # Handle IPv6 host
            if ':' in hostname and not hostname.startswith('['):
                hostname_formatted = f'[{hostname}]'
            else:
                hostname_formatted = hostname

            netloc = f"{hostname_formatted}:{port}"
            new_parsed = parsed._replace(netloc=netloc)
            result_urls.append(urlunparse(new_parsed))

        return result_urls

    @staticmethod
    def add_paths(url: str, paths: Optional[List[str]] = None) -> List[str]:
        if not paths:
            return [url]

        parsed = urlparse(url)
        result_urls = []

        for path in paths:
            normalized_path = path if path.startswith('/') else f"/{path}"
            new_parsed = parsed._replace(path=normalized_path)
            result_urls.append(urlunparse(new_parsed))

        return result_urls

    @staticmethod
    def expand_url(
        url: str,
        ports: Optional[List[int]] = None,
        paths: Optional[List[str]] = None,
        default_scheme: str = "https"
    ) -> List[str]:
        """
        Expands a base URL with combinations of optional ports and paths.
        - Ensures scheme
        - Supports IPv6
        - Returns list of full URLs
        """
        base_url = UrlUtils.ensure_scheme(url, default_scheme)
        urls_with_ports = UrlUtils.add_ports(base_url, ports)

        final_urls = []
        for port_url in urls_with_ports:
            expanded = UrlUtils.add_paths(port_url, paths)
            final_urls.extend(expanded)

        return final_urls

    @staticmethod
    def parse_url_parts(url: str) -> dict:
        parsed = urlparse(url)
        return {
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "path": parsed.path,
            "query": parsed.query,
            "fragment": parsed.fragment,
            "username": parsed.username,
            "password": parsed.password,
        }

    @staticmethod
    def replace_path(url: str, new_path: str) -> str:
        parsed = urlparse(url)
        return urlunparse(parsed._replace(path=new_path))

    @staticmethod
    def strip_url(url: str, keep: List[str] = ["scheme", "netloc", "path"]) -> str:
        parsed = urlparse(url)
        parts = {k: "" for k in ["scheme", "netloc", "path", "params", "query", "fragment"]}
        for k in keep:
            parts[k] = getattr(parsed, k)
        return urlunparse((
            parts["scheme"],
            parts["netloc"],
            parts["path"],
            "",  # params
            parts["query"],
            parts["fragment"]
        ))

    @staticmethod
    def normalize_url(url: str) -> str:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/") or "/"
        return urlunparse((scheme, netloc, path, "", "", ""))

    @staticmethod
    def extract_root_domain(url: str) -> str:
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def get_auth_from_url(url: str) -> Optional[Tuple[str, str]]:
        parsed = urlparse(url)
        if parsed.username and parsed.password:
            return parsed.username, parsed.password
        return None

    @staticmethod
    def append_query_params(url: str, params: dict) -> str:
        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        existing_params.update(params)
        new_query = urlencode(existing_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))