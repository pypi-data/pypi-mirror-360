import typing
from ..expression.assignable import Assignable
from .command import Command
from ..environment import Environment


class Assign(Command):
    def __init__(self, lhs: typing.Union[Assignable, tuple], rhs: typing.Any):
        self.lhs = lhs
        self.rhs = rhs

    def execute(self, env: Environment):
        value = env.evaluate(self.rhs)
        if not isinstance(self.lhs, tuple):
            self.lhs.assign(value, env)
            return
        for lhs, val in zip(self.lhs, value):  # type: ignore
            lhs.assign(val, env)
