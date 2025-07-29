import typing
from .address import Address
from .block_result import BlockResult
from .element import Element
from .index import Index
from .namespace import GlobalScope, Namespace


class NextLineCalculation:
    def __init__(self, block_result: BlockResult, processing_line: int):
        self.block_result = block_result
        self.processing_line = processing_line


class Environment:
    def __init__(self, code: list):
        from .block import Block

        self.code: list[list[Element]] = code
        self.addr = Address(1, 0)
        self.blocks: list[Block] = []
        self.callstack: list[Namespace] = []

        self.global_context = GlobalScope(None, {})
        self.context: Namespace = self.global_context

        self.prompt = ""
        self.returned_value: typing.Any = None

    def evaluate(self, obj: typing.Any) -> typing.Any:
        # to avoid circular imports, these must write here
        from .expression.assignable import Assignable
        from .expression.call import Call
        from .expression.operator import UnaryOperator, BinaryOperator

        if isinstance(obj, Assignable):
            return obj.evaluate(self)
        if isinstance(obj, BinaryOperator):
            return obj.evaluate(self)
        if isinstance(obj, Call):
            return obj.evaluate(self)
        if isinstance(obj, UnaryOperator):
            return obj.evaluate(self)
        if isinstance(obj, list):
            return [self.evaluate(elem) for elem in obj]
        if isinstance(obj, dict):
            return {key: self.evaluate(value) for key, value in obj.items()}
        if isinstance(obj, tuple):
            return tuple(self.evaluate(elem) for elem in obj)
        if isinstance(obj, set):
            return {self.evaluate(elem) for elem in obj}
        return obj

    def update_addr_to_next_command(self) -> None:
        next_line_index = 0
        while True:
            next_line_index = self.addr.line + 1
            calculating_next_line = self._pop_blocks(next_line_index)
            next_line_index = calculating_next_line.processing_line
            if calculating_next_line.block_result == BlockResult.SHIFT:
                break
        self.addr.line = next_line_index

    def _pop_blocks(self, line_index: int) -> NextLineCalculation:
        working_line = line_index
        while True:
            next_line: list[Element] = self.code[working_line]
            next_indent: int = next_line[Index.INDENT]  # type: ignore
            delta_indent = self.addr.indent - next_indent
            if delta_indent < 0:
                working_line += 1
                continue
            for _ in range(delta_indent):
                block = self.blocks[-1]
                block_result = block.did_exit(self)
                if block_result == BlockResult.JUMP:
                    return NextLineCalculation(BlockResult.JUMP, working_line)
            return NextLineCalculation(BlockResult.SHIFT, working_line)
