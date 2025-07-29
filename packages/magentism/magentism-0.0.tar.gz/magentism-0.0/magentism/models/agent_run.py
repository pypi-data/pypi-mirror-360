import json
import logging
from typing import Optional
from collections import defaultdict
from functools import cache

from pydantic import Field as PydanticField, BaseModel as PydanticBaseModel
from pydantic_core import ValidationError as PydanticValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ormantism import Base

from .agent import Agent, AgentRunConfig


SYSTEM_PROMPT_SUFFIX = """
Do not hesitate to 'think out loud' before calling tools.
To answer the user, you HAVE TO call the `stop` tool (be careful to provide parameters with the appropriate type).
"""

logger = logging.getLogger("agent_run")


class AgentStopException(Exception):
    def __init__(self, result: PydanticBaseModel):
        self.result = result
        super().__init__("Agent stopped")

class AgentInvalidStopException(Exception):
    def __init__(self, result: dict):
        self.result = result
        super().__init__("Agent wanted to stop, but provided invalid parameters")


class AgentRun(Base):
    caller: Optional["AgentRun"] = None
    agent: Agent
    initial_prompt: str
    config: AgentRunConfig = PydanticField(default_factory=AgentRunConfig)
    conversation: list[dict[str, str]] = PydanticField(default_factory=list)
    has_started: bool = False
    has_finished: bool = False
    messages: list[dict[str, any]] = PydanticField(default_factory=list)
    exception_class: str|None = None
    exception_message: str|None = None
    current_iteration: int = 0
    result: PydanticBaseModel|None = None

    @property
    @cache
    def model_with_tools(self):
        return self.agent.model_with_tools
    
    def _invoke_once(self):
        return self.model_with_tools.invoke(self.messages)

    def _call_tool(self, tool_call):
        tool_name = tool_call["name"].lower()
        tool_args = tool_call["args"]
        # special case: final call
        if tool_name == "stop":
            self._stop(**tool_args)
        # find tools in provided ones
        tool = self.agent.tools_for_execution.get(tool_name, None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found.")
        # execute
        return tool(**tool_args)
    
    def _stop(self, **kwargs):
        try:
            result = self.agent.return_type(**kwargs)
            raise AgentStopException(result)
        except PydanticValidationError as e:
            errors_by_parameter = defaultdict(list)
            for error in e.errors():
                path = ".".join(error["loc"][:-1])
                errors_by_parameter[path].append(error["msg"])
            raise AgentInvalidStopException({
                "error": "Invalid parameters",
                "validation_errors": [
                    {"parameter": parameter,
                    "errors": messages}
                    for parameter, messages in errors_by_parameter.items()
                ]
            })

    def resume(self):
        if not self.messages:
            self.messages = [
                {"role": "system", "content": self.agent.system_prompt + SYSTEM_PROMPT_SUFFIX},
                {"role": "user", "content": self.initial_prompt},
            ]
        self.has_started = True
        if self.has_finished:
            return
        for self.current_iteration in range(self.config.max_iterations):
                if self.messages[-1]["role"] != "assistant":
                    response = self._invoke_once()
                    logger.info("LLM says: %s", response.content)
                    self.messages = self.messages + [{
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": response.tool_calls,
                    }]
                for tool_call in self.messages[-1]["tool_calls"]:
                    try:
                        logger.info("LLM uses tool: #%s -> %s(%s)",
                                    tool_call["id"],
                                    tool_call["name"],
                                    ", ".join(f"{key}={json.dumps(value)}"
                                            for key, value
                                            in tool_call["args"].items()))
                        tool_response = self._call_tool(tool_call)
                        logger.info("LLM tool result: #%s -> %s",
                                    tool_call["id"],
                                    tool_response)
                        self.messages = self.messages + [{
                            "role": "tool",
                            "content": tool_response,
                            "tool_call_id": tool_call["id"]
                        }]
                    except AgentInvalidStopException as e:
                        self.messages = self.messages + [{
                            "role": "tool",
                            "content": e.result,
                            "tool_call_id": tool_call["id"]
                        }]
                    except AgentStopException as e:
                        self.update(has_finished=True,
                                    result=e.result)
                        return e.result
        # except Exception as e:
        #     self.update(has_finished=True,
        #                 exception_class=f"{e.__class__.__module__}.{e.__class__.__name__}",
        #                 exception_message=str(e.args[0]))
        #     raise


if __name__ == "__main__":
    import ormantism
    from pydantic import BaseModel as PydanticBaseModel
    ormantism.connect("sqlite://:memory:")

    class ReturnType(PydanticBaseModel):
        success: bool
        result: float | int
        error_message: str| None

    agent = Agent(name="Smith",
                  model_name="mistral",
                  tools=["tools.calculate"],
                  system_prompt="Perform calculations to answer the user's question.\n"
                                "Start by clarifying the user's intent, then elaborate how to solve the problem.\n",
                  return_type=ReturnType)
    agent.run("Given there's roughly 7B humans on Earth, that a human body has between 20 and 40 trillion cells, each containing 23 pairs of chromosomes... tell me how many human chromosomes there is on this planet ;)")

