from abc import ABC, abstractmethod
from typing import Any, Dict


class ResponseParser(ABC):

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def parse_response(response: Dict[str, Any]):
        pass
