import typing
from ..block import Block, BlockKind
from ..block_result import BlockResult
from .command import Command
from ..environment import Environment
from ..error import (
    InvalidBreakError,
    InvalidContinueError,
    ObjectNotIterableError,
)
from ..expression.assignable import Assignable


class For(Command):
    def __init__(
        self,
        vars: typing.Union[Assignable, tuple],
        iterable: typing.Any,
    ):
        self.vars = vars
        self.iterable = iterable

    def execute(self, env: Environment) -> None:
        try:
            value = env.evaluate(self.iterable)
            iterator = iter(value)
        except TypeError:
            raise ObjectNotIterableError(str(self.iterable))

        def enter(env: Environment) -> bool:
            try:
                value = next(iterator)
            except StopIteration:
                return False
            if isinstance(self.vars, tuple):
                for var, val in zip(self.vars, value):
                    var.assign(val, env)
                return True
            self.vars.assign(value, env)
            return True

        def exit(env: Environment) -> BlockResult:
            block.will_enter(env)
            return BlockResult.JUMP

        block = Block(BlockKind.FOR, env.addr, enter, exit)
        block.will_enter(env)


class While(Command):
    def __init__(self, condition: typing.Any):
        self.condition = condition

    def execute(self, env: Environment) -> None:
        def enter(env: Environment) -> bool:
            return env.evaluate(self.condition)

        def exit(env: Environment) -> BlockResult:
            block.will_enter(env)
            return BlockResult.JUMP

        block = Block(BlockKind.WHILE, env.addr, enter, exit)
        block.will_enter(env)


class Break(Command):
    def execute(self, env: Environment) -> None:
        while True:
            block = env.blocks.pop()
            if block.kind in (BlockKind.IFS, BlockKind.IF_ELIF_ELSE):
                env.addr.shift(-1)
                continue
            elif block.kind in (BlockKind.FOR, BlockKind.WHILE):
                env.addr.shift(-1)
                break
            else:
                raise InvalidBreakError()


class Continue(Command):
    def execute(self, env: Environment) -> None:
        while True:
            block = env.blocks.pop()
            if block.kind in (BlockKind.IFS, BlockKind.IF_ELIF_ELSE):
                env.addr.shift(-1)
                continue
            elif block.kind in (BlockKind.FOR, BlockKind.WHILE):
                block.will_enter(env)
                break
            else:
                raise InvalidContinueError()
