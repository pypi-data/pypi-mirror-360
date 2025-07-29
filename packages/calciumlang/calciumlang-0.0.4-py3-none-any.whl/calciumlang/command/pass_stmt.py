from .command import Command
from ..environment import Environment


class Comment(Command):
    def execute(self, env: Environment) -> None:
        pass  # do nothing


class Pass(Command):
    def execute(self, env: Environment) -> None:
        pass  # do nothing


class End(Command):
    def execute(self, env: Environment) -> None:
        pass  # do nothing
