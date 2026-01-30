from abc import ABC, abstractmethod

class LogicExecutor(ABC):
    @abstractmethod
    def executeModification(self):
        pass