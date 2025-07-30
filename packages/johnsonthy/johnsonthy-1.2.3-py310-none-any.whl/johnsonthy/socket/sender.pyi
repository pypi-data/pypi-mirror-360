# Stub file for type hints

import queue
from typing import Callable, Any
from johnsonthy.thread import Runnable
from johnsonthy.logging import LOGGER
from socket import socket

timeout: int: ...
separator: str: ...
class Sender:
    def __init__(self, *args, **kwargs): ...
    def run(self, *args, **kwargs): ...

