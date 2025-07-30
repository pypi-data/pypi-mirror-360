from beartype.claw import beartype_this_package

beartype_this_package()

import importlib.metadata

from .awscrllm import CRLLM
from .modules.agent import Agent
from .modules.chat import Chat
from .modules.chunk import Chunk
from .modules.dataset import DataSet
from .modules.document import Document
from .modules.session import Session

__version__ = importlib.metadata.version("aws_crllm")

__all__ = ["CRLLM", "DataSet", "Chat", "Session", "Document", "Chunk", "Agent"]

