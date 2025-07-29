import typing
from .command import Command
from ..environment import Environment


class ExprStmt(Command):
    def __init__(self, expr: typing.Any):
        self.expr = expr

    def execute(self, env: Environment) -> None:
        env.evaluate(self.expr)
