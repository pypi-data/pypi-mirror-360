from typing import Any
import requests
import logging

from config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)


def get_place_details(place_id: str) -> dict[str, str|int|None] | None:
    """Get detailed information about a specific place using its Google Places ID.
    
    Args:
        place_id: The unique Google Places ID for the location (e.g., "ChIJN1t_tDeuEmsRUsoyG83frY4")
    
    Returns:
        Dictionary with place details including id, name, address, rating, website, description, 
        opening_hours, and phone_number. Returns None if the place is not found or request fails.
    """
    try:
        response = requests.get(url=f"https://places.googleapis.com/v1/places/{place_id}",
                                params=dict(languageCode="fr"),
                                headers={
                                    "X-Goog-FieldMask": "id,displayName,addressComponents,editorial_summary,websiteUri,regularOpeningHours,rating,internationalPhoneNumber,location",
                                    "X-Goog-Api-Key": GOOGLE_API_KEY,
                                },
                                timeout=10)
        response.raise_for_status()
        data = response.json()
        #
        # "address": {
        #     "natural_feature": "Lac du Malsaucy",
        #     "locality": "Évette-Salbert",
        #     "administrative_area_level_2": "Territoire de Belfort",
        #     "administrative_area_level_1": "Bourgogne-Franche-Comté",
        #     "country": "France",
        #     "postal_code": "90350"
        # },
        #
        # "address": {
        #     "premise": "153 bis",
        #     "street_number": "153",
        #     "route": "Rue Paul Vaillant Couturier",
        #     "locality": "Alfortville",
        #     "administrative_area_level_2": "Val-de-Marne",
        #     "administrative_area_level_1": "Île-de-France",
        #     "country": "France",
        #     "postal_code": "94140"
        # },
        #
        print(data)
        exit()
        return {
            "google_place_id": data["id"],
            "name": data["displayName"]["text"],
            "address": {
                item["types"][0]: item["longText"]
                for item in data["addressComponents"]
            } | {
                "latitude": data["location"]["latitude"],
                "longitude": data["location"]["longitude"],
            },
            "rating": data.get("rating"),
            "website": data.get("websiteUri"),
            "description": data.get("editorialSummary", {}).get("text"),
            "opening_hours": data.get("regularOpeningHours", {}).get("periods"),
            "phone_number": data.get("internationalPhoneNumber"),
        }
    
    except Exception as e:
        logger.error(f"%s: %s", e.__class__.__name__, str(e))
        return None


def find_places(search_query: str) -> list[dict[str, str|None]] | None:
    """Find places matching a search query using Google Places API.
    
    Use this function to search for restaurants, attractions, businesses, or any location 
    based on a descriptive text query. The search works best with specific queries that 
    include location context.
    
    Args:
        search_query: Descriptive text to search for places (e.g., "Italian restaurants in Paris", 
                     "museums near Louvre", "cafes in Montmartre")
    
    Returns:
        List of matching places, each containing id, name, address, and optional description.
        Returns None if search fails or no results found.
        
    Example:
        find_places("pizza restaurants in Lyon") returns places with pizza in Lyon area.
    """    
    try:
        response = requests.post(url="https://places.googleapis.com/v1/places:searchText",
                                 headers={
                                     "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id,places.editorial_summary",
                                     "X-Goog-Api-Key": GOOGLE_API_KEY,
                                 },
                                 json={"textQuery": search_query,
                                       "languageCode": "fr"},
                                 timeout=10)
        response.raise_for_status()  # Raises exception for 4XX/5XX errors
        data = response.json()
        return [
            {
                "id": place_data["id"],
                "name": place_data["displayName"]["text"],
                "address": place_data["formattedAddress"],
                "description": place_data.get("editorialSummary", {}).get("text"),
            }
            for place_data in data["places"]
        ]
    
    except Exception as e:
        logger.error(f"%s: %s", e.__class__.__name__, str(e))
        return None


# Example usage
if __name__ == "__main__":
    import json
    
    # results = find_places("folies bergères")
    # print(json.dumps(results, indent=4))
    # print()
    
    # results = get_place_details("ChIJnZCBoxNu5kcRGir24woWYnQ") # New Morning
    # results = get_place_details("ChIJB_Ml9yk6kkcR08kH1gDxnTI") # Lac du Malsaucy
    # results = get_place_details("ChIJA0TW84E5kkcRvtgDM6cL2Ec") # Le Malsaucy
    # results = get_place_details("ChIJyxYKKAVz5kcRe4Wxadu2QAA") # Monoprix Alfortville
    results = get_place_details("ChIJE5NzzD9u5kcRQScUmbF4ZH8") # Folies Bergères
    print(json.dumps(results, indent=4))
    print()
