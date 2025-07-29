import typing
from ..block import Block, BlockKind
from ..block_result import BlockResult
from .command import Command
from ..environment import Environment


class Ifs(Command):
    def execute(self, env: Environment):
        def enter(env: Environment) -> bool:
            return True

        def exit(env: Environment) -> BlockResult:
            env.addr.shift(-1)
            return BlockResult.SHIFT

        block = Block(BlockKind.IFS, env.addr, enter, exit)
        block.will_enter(env)


def _execute_conditional_block(env: Environment) -> None:
    def enter(env: Environment) -> bool:
        return True

    def exit(env: Environment) -> BlockResult:
        env.addr.shift(-2)
        env.blocks.pop()
        return BlockResult.JUMP

    block = Block(BlockKind.IF_ELIF_ELSE, env.addr, enter, exit)
    block.will_enter(env)


class If(Command):
    def __init__(self, condition: typing.Any):
        self.condition = condition

    def execute(self, env: Environment):
        if env.evaluate(self.condition):
            _execute_conditional_block(env)


class Elif(If):
    pass


class Else(Command):
    def execute(self, env: Environment):
        _execute_conditional_block(env)
