from typing import Dict, Optional

class BaseRestConfig:
    """Base configuration class for REST clients"""
    headers: Dict[str, str] = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,vi;q=0.7,cs;q=0.6,th;q=0.5',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': '',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': '',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }

    def __init__(self, site: str, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.site = site
        self.base_url = base_url
        if site is not None:
            self.headers['origin'] = site
            self.headers['referer'] = site if site.endswith(
                '/') else site + '/'

        if headers is not None and not isinstance(headers, dict):
            raise TypeError("headers must be a dictionary")
        if headers is not None:
            self.headers = {**self.headers, **(headers or {})}

