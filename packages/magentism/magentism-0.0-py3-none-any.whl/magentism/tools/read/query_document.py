from typing import Literal
from pydantic import BaseModel

from models.bots import Bot
from .fetch_page import fetch_page


class ExtractionResult(BaseModel):
    status: Literal["found_complete", "found_partial", "found_nothing", "error"]
    extracted_data: str | None = None
    suggested_urls: list[str] | None = None
    error: str | None = None


def query_document(query: str, document: str|None=None, document_url: str|None=None) -> ExtractionResult:
    """Query the specified document to extract specific information.
    
    This function uses an LLM to search through a text document and extract information
    that directly answers the given query. It can work with either text content directly
    or by fetching content from a URL.
    
    Args:
        query: The specific information to look for (e.g., "population of Ecuador", 
               "founding date", "CEO name")
        document: Text content to search through, or None if using document_url
        document_url: URL of a web page to fetch and search, or None if using document
        
    Returns:
        Object containing:
        - status: "found_complete", "found_partial", "found_nothing", or "error"
        - extracted_data: The found information (if any)
        - try_these_links: Suggested URLs that might contain the requested information
        - error: Error message if something went wrong
            
    Note:
        Exactly one of `document` or `document_url` must be provided, not both.
        
    Examples:
        >>> text = "Ecuador has a population of 17.8 million people as of 2023..."
        >>> result = query_document("population of Ecuador", document=text, document_url=None)
        >>> result.status
        "found_complete"
        >>> result.extracted_data
        "17.8 million"
        
        >>> result = query_document("population of Guayas in 2001", document=None, 
        ...                         document_url="https://en.wikipedia.org/wiki/Ecuador")
        >>> result.status
        "found_nothing"
        >>> result.suggested_urls
        ["https://www.ecuadorencifras.gob.ec/proyecciones-poblacionales/",
         "https://www.cia.gov/the-world-factbook/countries/ecuador/",
         "https://en.wikipedia.org/wiki/Demographics_of_Ecuador"]
    """
    bot = Bot("gemini")
    
    system_message = system_message = f"""You are an information extraction assistant. Your task is to analyze the given text and extract specific information.

Query: {query}

Instructions:
1. Carefully read through the provided text/document
2. Look for information that directly answers the query
3. Respond with a JSON object containing:
   - "status": one of "found_complete", "found_partial", "found_nothing", or "error"
   - "extracted_data": the extracted piece of information (if found), or null (if not found)
   - "suggested_urls": array of URLs/links mentioned in the document that might contain the queried data (if "status" is "found_partial" or "found_complete"), or null
   - "error": any error or issue encountered during extraction, or null

Status Guidelines:
- "found_complete": All requested information is clearly present in the document, and has been restituted in "extracted_data"
- "found_partial": Some but not all of the requested information is available, and returned in "extracted_data"
- "found_nothing": The requested information is not present in the document
- "error": An error occurred during processing

Extraction Guidelines:
- CRITICAL: Only extract information that is explicitly stated in the provided document
- Do NOT infer, assume, or add information that is not directly present in the text
- For "extracted_data", return only facts that can be directly quoted or referenced from the document
- Be CERTAIN that "extracted_data" directly answeres the query; if unsure, leave blank and provide "suggested_urls" if available, and/or set "status" to "found_partial" or "found_nothing"
- Return just the key facts, not full sentences unless necessary
- For "suggested_urls", look for URLs, references, or "see also" sections in the document that might help answering the query (three links tops)
- Return valid JSON format only"""

    if not (bool(document) ^ bool(document_url)):
        return ExtractionResult(status="error",
                                error="You should provide either `document` or `document_url` parameters, but not both.")
    if document_url:
        document = fetch_page(document_url)
        if isinstance(document, int):
            return ExtractionResult(status="error",
                                    error=f"Got a {document} HTTP response when retrieving {document_url}")
        if document is None:
            return ExtractionResult(status="error",
                                    error=f"Document at {document_url} is not a text document")

    response = bot.invoke([
        {"role": "system", "content": system_message},
        {"role": "user", "content": document}
    ])
    
    return response.content.strip()


if __name__ == "__main__":
    print(
        query_document("population of Ecuador",
                     "Ecuador, officially the Republic of Ecuador, is a country in northwestern South America, bordered by Colombia on the north, Peru on the east and south, and the Pacific Ocean on the west. It also includes the Galápagos Province which contains the Galapagos Islands in the Pacific, about 1,000 kilometers (621 mi) west of the mainland. The country's capital is Quito and its largest city is Guayaquil.\n\nThe land that comprises modern-day Ecuador was once home to several groups of indigenous peoples that were gradually incorporated into the Inca Empire during the 15th century. The territory was colonized by the Spanish Empire during the 16th century, achieving independence in 1820 as part of Gran Colombia, from which it emerged as a sovereign state in 1830. The legacy of both empires is reflected in Ecuador's ethnically diverse population, with most of its 17.8 million people being mestizos, followed by large minorities of Europeans, Native American, African, and Asian descendants. Spanish is the official language spoken by a majority of the population, although 13 native languages are also recognized, including Quechua and Shuar.",
                     None)
    )
    print(
        query_document("number of people living in Guayas in 2001",
                     None,
                     "https://en.wikipedia.org/wiki/Ecuador")
    )
    print(
        query_document("color of violets",
                     "Roses are red\nViolets are blue,\nSugar is sweet\nAnd so are you.",
                     None)
    )
    print(
        query_document("color of tulips",
                     "Roses are red\nViolets are blue,\nSugar is sweet\nAnd so are you.",
                     None)
    )
