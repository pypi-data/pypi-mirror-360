import requests
from ._logger import logger

from config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID


def web_search(search_query: str, result_limit: int = 5) -> list[dict[str, str]] | None:
    """
    Search the web for information and return structured results.
    
    Use this tool when you need to find current information, recent news, facts not in your 
    training data, or when the user explicitly asks you to search the web.
    
    Parameters:
        search_query (str): The search terms to look for. Use clear, specific keywords.
                           Examples: "Python pandas tutorial", "weather forecast Paris", 
                           "latest news artificial intelligence"
        result_limit (int): Number of search results to return. Default is 5, maximum is 10.
                           Use fewer results (3-5) for focused searches, more (8-10) for broader research.
    
    Returns:
        list[dict]: List of search results, each containing:
            - "title": Webpage title
            - "url": Direct link to the webpage  
            - "snippet": Brief preview of the page content
        None: If search fails due to API errors, network issues, or invalid queries
    
    Example usage:
        results = web_search("climate change 2024 report")
        results = web_search("restaurant reviews Tokyo", result_limit=8)
    """
    logger.debug(f"SEARCH_THE_WEB: {search_query}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": search_query,
        "num": min(result_limit, 10)  # Free tier max is 10 results per query
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises exception for 4XX/5XX errors
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Search error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    import sys
    results = search_the_web(sys.argv[1], max_results=5)
    # results = search_the_web("new morning 75004", max_results=5)
    if results:
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['link']}")
            print(f"Description: {result['snippet']}\n")
    else:
        print("Search failed")
