import logging
import time

import requests
from lxml import html as lxml_html

logger = logging.getLogger(__name__)


class CrawlerError(Exception):
    """Base exception for crawler errors."""
    pass


class MovieNotFoundError(CrawlerError):
    def __init__(self, source: str, query: str, detail: str = ''):
        self.source = source
        self.query = query
        super().__init__(f"[{source}] Movie not found: {query}" + (f" ({detail})" if detail else ''))


class NetworkError(CrawlerError):
    def __init__(self, source: str, url: str, status: int = None):
        msg = f"[{source}] Network error: {url}"
        if status:
            msg += f" (HTTP {status})"
        super().__init__(msg)


class Request:
    """HTTP client wrapper with retry, proxy, and rate-limiting support."""

    def __init__(self, proxy: str = None, timeout: int = 10, retry: int = 3):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        self.timeout = timeout
        self.retry = retry

    def get(self, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault('timeout', self.timeout)
        last_exc = None
        for attempt in range(1, self.retry + 1):
            try:
                resp = self.session.get(url, **kwargs)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                last_exc = e
                logger.debug(f"Request failed (attempt {attempt}/{self.retry}): {url} - {e}")
                if attempt < self.retry:
                    time.sleep(1 * attempt)
        raise NetworkError('HTTP', url) from last_exc

    def get_json(self, url: str, **kwargs) -> dict:
        resp = self.get(url, **kwargs)
        return resp.json()

    def get_html(self, url: str, **kwargs) -> lxml_html.HtmlElement:
        resp = self.get(url, **kwargs)
        return lxml_html.fromstring(resp.text)
