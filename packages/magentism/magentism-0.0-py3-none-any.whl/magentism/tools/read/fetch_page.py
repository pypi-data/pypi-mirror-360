import re
import requests
from ._logger import logger
from ._converter import Converter



HEADERS = {
    # Googlebot headers
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',  # Googlebot supports gzip, deflate, and Brotli
    'Connection': 'keep-alive',
    'From': 'googlebot(at)googlebot.com', # An email address for problem reports (though direct email responses are unlikely)
    # Caching-related headers, sent when re-crawling for efficiency:
    'If-Modified-Since': 'Fri, 01 Jan 2024 12:00:00 GMT', # Date of last modification Googlebot saw
    'If-None-Match': '"some-etag-value"', # ETag of the last content Googlebot saw
    # Other headers might appear depending on the specific crawl and content type:
    'Accept-Language': 'fr-FR,fr;q=0.9', # While less commonly mentioned for Googlebot, browsers send this.
                                        # Googlebot generally tries to render as a default user.
}
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/126.0',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
#     'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
# ]
# HEADERS = {
#     'User-Agent': random.choice(USER_AGENTS),
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'none', # Can be adjusted based on if you're coming from another site
#     'Sec-Fetch-User': '?1',
# }


def fetch_page(url: str) -> str:
    """Read the content of a web page from a URL, converted from HTML to MarkDown.
    """
    response = requests.get(url, headers=HEADERS)
    logger.debug(f"FETCH_PAGE {url} -> {response.status_code}")
    if response.status_code // 100 != 2:
        return response.status_code
    if response.headers.get("Content-Type", "").startswith("text/markdown"):
        return response.text
    if response.headers.get("Content-Type", "").startswith("text/plain"):
        return response.text
    if not response.headers.get("Content-Type", "").startswith("text/html"):
        return None
    html = response.text
    if "wikipedia.org/wiki" in url:
        html = response.text
        html = re.sub(r'<span class="vector-dropdown-label-text">.*?</span>', "", html)
        markdown = Converter(url).convert(html)
        markdown = markdown.split("\n* This page was last edited on ")[0]
        markdown = re.sub(r"\n+\[\[edit\][^\]]+\]\n+", "\n", markdown)
    else:
        markdown = Converter(url).convert(html)
        markdown = re.sub(r"\n{2,}", "\n\n", markdown)
    return markdown


if __name__ == "__main__":
    print(
        fetch_page("https://en.wikipedia.org/wiki/Guayaquil")
        # fetch_page("https://en.wikipedia.org/wiki/Ecology")
        # fetch_page("https://newmorning.com/")
    )