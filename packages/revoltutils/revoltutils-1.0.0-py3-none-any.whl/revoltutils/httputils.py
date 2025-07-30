import httpx
from fake_useragent import UserAgent
from requests.cookies import RequestsCookieJar
from typing import List,Optional,Tuple

class HttpUtils:

    @staticmethod
    def extract_cookies(cookie_jar: RequestsCookieJar) -> list[dict]:
        formatted_cookies = []
        if cookie_jar:
            for cookie in cookie_jar:
                cookie_data = {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "expires": cookie.expires,
                    "secure": cookie.secure,
                    "http_only": cookie.has_nonstandard_attr('HttpOnly')
                }
                formatted_cookies.append(cookie_data)
        return formatted_cookies

    @staticmethod
    def get_random_user_agent() -> str:
        return UserAgent().random
    @staticmethod
    def normalize_header(list_headers: list) -> dict:
        headers = {}
        for header_str in list_headers:
            try:
                name, value = header_str.split(':', 1)
                headers[name.strip()] = value.strip()
            except ValueError:
                pass
        return headers

    @staticmethod
    def all_http_methods() -> List[str]:
        return [
            "GET", "HEAD", "POST", "PUT",
            "PATCH", "DELETE", "CONNECT", "OPTIONS", "TRACE"
        ]

    @staticmethod
    async def dump_request(request: httpx.Request) -> str:
        """
        Construct the raw HTTP request from httpx.Request object.
        """
        method = request.method.upper()
        path = request.url.path or "/"
        query = f"?{request.url.query}" if request.url.query else ""
        version = "HTTP/1.1"

        request_line = f"{method} {path}{query} {version}"
        headers = "\r\n".join(f"{k}: {v}" for k, v in request.headers.items())

        body = ""
        if request.content:
            if isinstance(request.content, (bytes, bytearray)):
                body = request.content.decode(errors="ignore")
            else:
                body = str(request.content)

        raw = f"{request_line}\r\n{headers}\r\n\r\n{body}"
        return raw.strip()

    @staticmethod
    async def dump_response(response: httpx.Response) -> str:
        """
        Construct the raw HTTP response from httpx.Response object.
        """
        version = f"{response.http_version or 'HTTP/1.1'}"
        status_line = f"{version} {response.status_code} {response.reason_phrase}"

        headers = "\r\n".join(f"{k}: {v}" for k, v in response.headers.items())
        body = response.text

        raw = f"{status_line}\r\n{headers}\r\n\r\n{body}"
        return raw.strip()

    @staticmethod
    async def dump_response_headers_and_raw(response: httpx.Response) -> Tuple[str, str]:
        """
        Returns tuple of (headers_only, full_response).
        """
        raw = await HttpUtils.dump_response(response)
        header_section, _, _ = raw.partition("\r\n\r\n")
        return header_section, raw

    @staticmethod
    def raw_request_builder(
            method: str,
            url: str,
            headers: Optional[dict] = None,
            body: Optional[str] = None,
            version: str = "HTTP/1.1"
    ) -> str:
        """
        Manually build raw HTTP request string.
        """
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        request_line = f"{method.upper()} {path} {version}"
        headers_section = "\r\n".join(f"{k}: {v}" for k, v in (headers or {}).items())

        return f"{request_line}\r\n{headers_section}\r\n\r\n{body or ''}".strip()

    @staticmethod
    def raw_response_builder(
            status_code: int,
            reason: str = "OK",
            headers: Optional[dict] = None,
            body: Optional[str] = None,
            version: str = "HTTP/1.1"
    ) -> str:
        """
        Manually build raw HTTP response string.
        """
        status_line = f"{version} {status_code} {reason}"
        headers_section = "\r\n".join(f"{k}: {v}" for k, v in (headers or {}).items())
        return f"{status_line}\r\n{headers_section}\r\n\r\n{body or ''}".strip()

    @staticmethod
    async def raw_http_reader(raw_http: str):
        lines = raw_http.splitlines()
        request_line = lines[0].split()
        method = request_line[0]
        url = request_line[1]

        headers = {}
        i = 1
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
            i += 1
        body = ""
        if i + 1 < len(lines):
            body = '\n'.join(lines[i + 1:]).strip()
        return method, url, headers, body