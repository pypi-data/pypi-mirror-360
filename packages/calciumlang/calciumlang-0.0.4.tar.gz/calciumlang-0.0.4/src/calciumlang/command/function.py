import typing
from ..block import Block, BlockKind
from ..block_result import BlockResult
from .command import Command
from ..environment import Environment
from ..error import InvalidReturnError
from ..label import FunctionCalled
from ..namespace import ClassScope, FuncScope


class Def(Command):
    def __init__(self, name: str, params: list[str]):
        self.name = name
        self.params = params

    def execute(self, env: Environment) -> None:
        defined_addr = env.addr.clone()
        nesting_scope = env.context.find_nesting_scope()
        is_classscope = isinstance(env.context, ClassScope)
        is_init = self.name == "__init__" and is_classscope

        def _func(*args, is_called_by_library=True):
            # could be called by standard library
            caller_addr = env.addr.clone()
            local = FuncScope(
                nesting_scope,
                {param_name: arg for param_name, arg in zip(self.params, args)},
            )
            callee_addr = defined_addr.clone()
            callee_addr.calls = caller_addr.calls + 1

            def enter(env: Environment) -> bool:
                env.callstack.append(env.context)
                env.context = local
                return True

            had_exited = False

            def exit(env: Environment) -> BlockResult:
                env.addr.jump(caller_addr)
                env.addr.calls -= 1
                env.addr.shift(0, -1)
                if is_init:
                    env.returned_value = env.context.lookup("self")
                env.context = env.callstack.pop()
                nonlocal had_exited
                had_exited = True
                return BlockResult.JUMP

            block = Block(BlockKind.CALL, callee_addr, enter, exit)
            block.will_enter(env)

            if not is_called_by_library:
                # controls the flow of the program
                raise FunctionCalled()

            from ..parser import Parser

            parser = Parser()
            while not had_exited:
                env.update_addr_to_next_command()
                last_index = len(env.code) - 1
                if env.addr.indent == 0:
                    break
                if env.addr.line >= last_index:
                    break
                line = env.code[env.addr.line]
                cmd = parser.read(line)
                cmd.execute(env)
            env.update_addr_to_next_command()
            value = env.returned_value
            env.returned_value = None
            return value

        env.context.define(self.name, _func)


class Return(Command):
    def __init__(self, expr: typing.Any):
        self.expr = expr

    def execute(self, env: Environment) -> None:
        env.returned_value = env.evaluate(self.expr)
        while True:
            block = env.blocks[-1]
            if block.kind == BlockKind.CALL:
                block.did_exit(env)
                return
            if block.kind in (
                BlockKind.IFS,
                BlockKind.IF_ELIF_ELSE,
                BlockKind.FOR,
                BlockKind.WHILE,
            ):
                env.blocks.pop()
                continue
            raise InvalidReturnError()
