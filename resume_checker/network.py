from typing import List

import requests


def _url_checker(urls: List[str]) -> List[str]:
    broken_urls = []
    for index, url in enumerate(urls):
        if "mailto" not in url:
            print(f"Checking {index} of {len(urls)} urls", end="\r", flush=True)
            try:
                r = requests.head(url)
                if r.status_code == 404 or r.status_code == 503:
                    broken_urls.append(url)
            except requests.exceptions.RequestException:
                broken_urls.append(url)
    return broken_urls
