from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, comment: str, context: str, code_block: str) -> str:
        pass



