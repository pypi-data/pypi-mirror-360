import abc

from ..environment import Environment


class Command(abc.ABC):
    @abc.abstractmethod
    def execute(self, env: Environment) -> None:
        pass
