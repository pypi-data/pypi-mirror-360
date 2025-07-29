import enum

from config import DATABASE_URL
from ._base import Base
from .agent import Agent


class ActionType(enum.Enum):
    START = "start"
    WRITE = "write"
    CALL = "call"
    RECEIVE = "receive"
    EXIT = "exit"

class Action(Base):
    agent: Agent
    type: ActionType
    data: str | dict[str, str|dict|list|int|float|None] | None
