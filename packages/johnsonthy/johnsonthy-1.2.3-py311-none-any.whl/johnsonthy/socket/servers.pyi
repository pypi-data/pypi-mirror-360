# Stub file for type hints

import socket
import queue
import time
from typing import List
from johnsonthy.logging import LOGGER
from johnsonthy.thread import Runnable, ThreadPoolHandler
from handlers.receiver import Receiver
from handlers.sender import Sender

class Servers:
    def __init__(self, *args, **kwargs): ...
    def init_server(self, *args, **kwargs): ...
    def stop_server(self, *args, **kwargs): ...
    def simulate_scanning(self, *args, **kwargs): ...

