import enum
import typing
from .address import Address
from .block_result import BlockResult
from .environment import Environment


class BlockKind(enum.Enum):
    IFS = 0
    IF_ELIF_ELSE = 1

    FOR = 2
    WHILE = 3

    CALL = 4

    CLASS = 5


class Block:
    def __init__(
        self,
        kind: BlockKind,
        addr: Address,
        enter: typing.Callable[[Environment], bool],
        exit: typing.Callable[[Environment], BlockResult],
    ):
        self.kind = kind
        self.addr = addr.clone()
        self.enter = enter
        self.exit = exit

    def will_enter(self, env: Environment):
        env.addr = self.addr.clone()
        if self.enter(env):
            env.addr.shift(1)
            env.blocks.append(self)

    def did_exit(self, env: Environment) -> BlockResult:
        env.blocks.pop()
        return self.exit(env)
