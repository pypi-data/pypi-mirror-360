from dataclasses import dataclass
import importlib
import os

from httpx import HTTPStatusError
from langchain_core.language_models.chat_models import BaseChatModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import config


def _import_from_path(path: str):
    module_path, class_name = path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

@dataclass
class Bot:

    name: str
    chat_model: BaseChatModel

    def __post_init__(self) -> "Bot":
        for bot_config in config.get("bots"):
            if bot_config["name"] == self.name:
                if bot_config["class"].endswith(".ChatMistralAI"):
                    if "MISTRAL_API_KEY" not in os.environ:
                        os.environ["MISTRAL_API_KEY"] = bot_config["parameters"]["api_key"]
                chat_model_class = _import_from_path(bot_config["class"])
                chat_model = chat_model_class(max_retries=10, **bot_config["parameters"])
                return Bot(chat_model=chat_model)
        raise ValueError(f"No bot with name {repr(self.name)} was found in config.yaml")

    @retry(
        stop=stop_after_attempt(8),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((HTTPStatusError, ConnectionError, TimeoutError))
    )
    def invoke(self, *args, **kwargs):
        return self.chat_model.invoke(*args, **kwargs)
