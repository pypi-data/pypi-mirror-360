import re
import requests
import wikipediaapi

from ._logger import logger
from ._converter import Converter

USER_AGENT = "SOLUTION_FINDER (mathieu+wiki@rodic.fr)"
HEADERS = {
    # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'User-Agent': USER_AGENT
}

def wikipedia_search(query: str, max_results: int, language_code: str) -> list[dict[str, str]] | None:
    """
    Searches Wikipedia and returns results.
    Results are meant to be passed to `fetch_wikipedia_page` when possibly relevant.
    
    Args:
        query: Search query string (use the fewest possible amount of keywords)
        max_results: Maximum number of results to return
        language: two-letters language code
    
    Returns:
        List of search result dictionaries with "title", "url" and "snippet" keys.
        Returns None on errors.
    """
    url = f"https://api.wikimedia.org/core/v1/wikipedia/{language_code}/search/page"
    parameters = {"q": query, "limit": max_results}
    response = requests.get(url, headers=HEADERS, params=parameters)
    logger.debug(f"SEARCH_WIKIPEDIA: {query} -> {len(response.json())} results")
    return [
        {
            "title": page["title"],
            "url": f"https://{language_code}.wikipedia.org/wiki/{page['key']}",
            "snippet": page["excerpt"].replace('<span class="searchmatch">', '*').replace('</span>', '*'),
        }
        for page in response.json()["pages"]
    ]


def fetch_wikipedia_page(title: str, language_code: str) -> str|None:
    """Fetch a page from Wikipedia in markdown format, given its title and the two-letters language code
    """
    wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT,
                                  language=language_code,
                                  extract_format=wikipediaapi.ExtractFormat.HTML)
    # page = wiki.page(title)
    logger.debug(f"FETCH_WIKIPEDIA_PAGE: {title}, {language_code}")
    url = f"https://{language_code}.wikipedia.org/wiki/{title}"
    response = requests.get(url, headers=HEADERS)
    html = response.text
    html = re.sub(r'<span class="vector-dropdown-label-text">.*?</span>', "", html)
    markdown = Converter(url, False).convert(html)
    markdown = markdown.split("\n* This page was last edited on ")[0]
    markdown = re.sub(r"\n+\[\[edit\][^\]]+\]\n+", "\n", markdown)
    # markdown = markdown.split("Contents\n--------")[1]
    markdown = markdown.replace("\nmove to sidebar\nhide\n", "\n")
    return markdown


# Example usage
if __name__ == "__main__":
    import json
    print(
        json.dumps(
            wikipedia_search("tree roots", 10, "en"),
            indent=4
        )
    )