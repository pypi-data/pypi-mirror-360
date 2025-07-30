# Stub file for type hints

import queue
from typing import Callable as _Callable, Any as _Any
from johnsonthy.thread.handler import Runnable as _Runnable
from johnsonthy.logging import LOGGER as _LOGGER
from socket import socket

timeout: int: ...
separator: str: ...
class Sender:
    def __init__(self, *args, **kwargs): ...
    def run(self, *args, **kwargs): ...

