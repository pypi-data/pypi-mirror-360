import typing
from ..environment import Environment
from ..keyword import Keyword
from ..error import OperatorNotSupportedError


class BinaryOperator:
    def __init__(self, op: Keyword, left: typing.Any, right: typing.Any):
        self.op = op
        self.left = left
        self.right = right

    def evaluate(self, env: Environment) -> typing.Any:
        l = env.evaluate(self.left)
        r = env.evaluate(self.right)
        if self.op == Keyword.ADD:
            return l + r
        if self.op == Keyword.SUBTRACT:
            return l - r
        if self.op == Keyword.MULTIPLY:
            return l * r
        if self.op == Keyword.DIVIDE:
            return l / r
        if self.op == Keyword.FLOOR_DIVIDE:
            return l // r
        if self.op == Keyword.MODULO:
            return l % r
        if self.op == Keyword.POWER:
            return l**r

        if self.op == Keyword.EQUAL:
            return l == r
        if self.op == Keyword.NOT_EQUAL:
            return l != r
        if self.op == Keyword.LESS_THAN:
            return l < r
        if self.op == Keyword.LESS_THAN_EQUAL:
            return l <= r
        if self.op == Keyword.GREATER_THAN:
            return l > r
        if self.op == Keyword.GREATER_THAN_EQUAL:
            return l >= r

        if self.op == Keyword.AND:
            return l and r
        if self.op == Keyword.OR:
            return l or r

        if self.op == Keyword.IN:
            return l in r
        raise OperatorNotSupportedError(self.op)


class UnaryOperator:
    def __init__(self, op: Keyword, operand: typing.Any) -> None:
        self.op = op
        self.operand = operand

    def evaluate(self, env: Environment) -> typing.Any:
        value = env.evaluate(self.operand)
        if self.op == Keyword.NEGATIVE:
            return -value
        if self.op == Keyword.NOT:
            return not value
        raise OperatorNotSupportedError(self.op)
