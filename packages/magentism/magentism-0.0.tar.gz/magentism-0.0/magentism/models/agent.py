import importlib
from typing import Optional
from functools import cache

from pydantic import BaseModel as PydanticBaseModel, Field as PydanticField
from langchain_core.tools import create_schema_from_function
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.tools import BaseTool
from langchain.chat_models.base import init_chat_model
from ormantism import Base

import config


class AgentRunConfig(PydanticBaseModel):
    max_iterations: int = 10
    temperature: float = 0.3
    multiple_tool_calls: bool = True

    def __or__(self, other: "AgentRunConfig") -> "AgentRunConfig":
        if other is None:
            return self
        return AgentRunConfig(**(
            self.model_dump() | other.model_dump()
        ))
    

class AgentStopTool(BaseTool):
    name: str = "stop"
    description: str = "Stop working and return the result"
    return_type: type[PydanticBaseModel] | None = None

    def __init__(self, return_type: type[PydanticBaseModel]):
        super().__init__(args_schema=return_type)

    def _run(self, **kwargs):
        """Should never be called.
        """


class Agent(Base):
    maker: Optional["Agent"] = None
    name: str
    model_name: str
    tools: list[str]
    system_prompt: str
    return_type: type[PydanticBaseModel]
    default_run_config: AgentRunConfig = PydanticField(default_factory=AgentRunConfig)

    def run(self, first_prompt: any, config: AgentRunConfig|None = None) -> "AgentRun":
        from .agent_run import AgentRun
        run = AgentRun(agent=self,
                       initial_prompt=first_prompt,
                       config=self.default_run_config | config)
        run.resume()
        return run
    
    @staticmethod
    def _import_tool(path: str):
        """Import and return a method/attribute given its full module path.
        
        Args:
            path: Full dotted path to the method/attribute (e.g., "os.path.join").
        
        Returns:
            The imported method/attribute.
        
        Raises:
            ImportError: If the module or attribute cannot be imported.
        """
        module_path, _, attr_name = path.rpartition('.')
        if not module_path:
            raise ImportError(f"Invalid path '{path}'; must be in format 'module.submodule.attribute'.")
        
        module = importlib.import_module(module_path)
        try:
            return getattr(module, attr_name)
        except AttributeError:
            raise ImportError(f"Attribute '{attr_name}' not found in module '{module_path}'.")

    @property
    @cache
    def tools_for_langchain(self) -> list[PydanticBaseModel]:
        return [
            create_schema_from_function(model_name=tool_path.rsplit(".")[-1],
                                        func=self._import_tool(tool_path),
                                        parse_docstring=False)
            for tool_path in self.tools
        ] + [AgentStopTool(self.return_type)]
    
    @property
    @cache
    def tools_for_execution(self) -> dict[str, callable]:
        return {
            tool_path.rsplit(".")[-1]: self._import_tool(tool_path)
            for tool_path in self.tools
        }

    @property
    def model(self) -> BaseChatModel:
        for model_config in config.get("models"):
            if model_config["name"] == self.model_name:
                return init_chat_model(**model_config["parameters"])
        raise NameError(f"No model described in `models` section of `config.yaml` with name `{self.model_name}`")

    @property
    def model_with_tools(self) -> BaseChatModel:
        return self.model.bind_tools(self.tools_for_langchain)


if __name__ == "__main__":
    import ormantism
    ormantism.connect(":memory:")

    class ReturnType(PydanticBaseModel):
        success: bool
        result: float | int
        error_message: str| None

    agent = Agent(name="Smith",
                  model_name="mistral",
                  tools=["tools.calculate"],
                  system_prompt="Perform calculations to answer the user's question.\n"
                                "Don't hesitate to 'think' out loud before using tools.",
                  return_type=ReturnType)
    
    agent = Agent.load(name="Smith", last_created=True)
    print()
    print(agent)
    print()
    print(agent.model.invoke("Hi :)"))
    print()
