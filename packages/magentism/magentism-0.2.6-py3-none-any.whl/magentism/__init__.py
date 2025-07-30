from .magentism.agent import Agent
from .magentism.agent_call import AgentCall
from .magentism.call_config import CallConfig
from .magentism.llm import LLM
from .magentism import tools
def set_database(database_url: str):
    from ormantism import connect
    connect(database_url)
