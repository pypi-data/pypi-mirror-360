from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from config import GEMINI_API_KEY
from .fetch_page import fetch_page



def _crawl(urls: list[str], instructions: str, llm: BaseChatModel, output_model: type[BaseModel], crawled_urls: set[str], max_depth=10) -> BaseModel:
    for url in urls:
        # fetch URL if not already done
        if url in crawled_urls:
            continue
        crawled = fetch_page.func(url)
        print(f"GET {url}")
        crawled_urls.add(url)
        if not isinstance(crawled, str):
            continue
        # use LLM to parse web page
        result = llm.invoke(instructions + crawled)
        # items found
        print(result.items)
        yield from (result.items or [])
        # further readings
        if max_depth:
            for url in result.further_reading_urls or []:
                yield from _crawl(urls=result.further_reading_urls,
                                  instructions=instructions,
                                  llm=llm,
                                  output_model=output_model,
                                  crawled_urls=crawled_urls,
                                  max_depth=max_depth-1)

def crawl(urls: list[str], item_plural_name: str, item_model: type[BaseModel], item_definition: str) -> BaseModel:
    class OutputModel(BaseModel):
        items: list[item_model]
        further_reading_urls: list[str]
    instructions = (f"Make a comprehensive inventory of the {item_plural_name} mentionned in the following document, extracted from a web page.\n\n"
                    f"Each of the {item_plural_name} found in the document should be an element in the output's `items`.\n\n"
                    f"Do NOT mention categories of {item_plural_name} `items`, only specific {item_plural_name}.\n\n"
                    f"{item_definition}"
                    f"Mention every web URL that could lead to retrieving more {item_plural_name} in the output's `further_reading_urls`.\n\n---\n\n")
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash-exp",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1
    )
    structured_llm = llm.with_structured_output(OutputModel)

    explored_urls = set()
    yield from _crawl(urls, instructions, structured_llm, OutputModel, explored_urls)


if __name__ == "__main__":
    class Conflict(BaseModel):
        name: str
        short_description: str
        parties_involved: list[str]
        year_start: int
        year_end: int
    results = crawl(urls=["https://acleddata.com/", "https://correlatesofwar.org/"],
                    item_plural_name="conflicts",
                    item_model=Conflict,
                    item_definition="A conflict can consist of a war, revolution or revolt, insurgency, isolated battle, small-scale conflict, military intervertion, terrorist act, genocide, civil war...)")
    for item in results:
        print(item.model_dump())