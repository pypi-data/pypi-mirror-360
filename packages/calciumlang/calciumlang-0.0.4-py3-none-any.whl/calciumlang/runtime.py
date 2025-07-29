import enum
import typing
import json

from .address import Address
from .command.command import Command
from .command.pass_stmt import End
from .element import Element
from .environment import Environment
from .index import Index
from .keyword import Keyword
from .label import FunctionCalled, InputCalled
from .parser import Parser


class RuntimeResult(enum.Enum):
    TERMINATED = 0
    EXECUTED = 1
    BREAKPOINT = 2
    EXCEPTION = 3
    PAUSED = 4


class Runtime:
    def __init__(self, code: typing.Union[str, list]):
        commands: list
        if isinstance(code, str):
            commands = json.loads(code)
        else:
            commands = code
        self.env = Environment(commands)
        self.breakpoints = set()
        self.parser = Parser()
        self._calls = []
        self._inputcmd: typing.Optional[Command] = None

    def resume(self, inputstr: str) -> RuntimeResult:
        """Resumes the runtime after an input() call."""
        self.env.returned_value = inputstr
        cmd: Command = self._inputcmd  # type: ignore
        self._inputcmd = None
        try:
            cmd.execute(self.env)
            self.env.update_addr_to_next_command()
        except FunctionCalled:
            caller_addr = self.env.addr.clone()
            self._calls.append(CallingCommand(caller_addr, cmd))
        except InputCalled:
            self._inputcmd = cmd
            return RuntimeResult.PAUSED
        except:
            raise
        return RuntimeResult.EXECUTED

    def run(self) -> RuntimeResult:
        while True:
            result = self.step()
            if result == RuntimeResult.EXECUTED:
                continue
            else:
                return result

    def step(self) -> RuntimeResult:
        last_index = len(self.env.code) - 1
        if self.env.addr.indent == 0:
            return RuntimeResult.TERMINATED
        if self.env.addr.line >= last_index:
            return RuntimeResult.TERMINATED

        line = self.env.code[self.env.addr.line]
        cmd = self.parser.read(line)

        caller_addr = self.env.addr.clone()
        if len(self._calls) > 0 and caller_addr.is_at(self._calls[-1].addr):
            last_called_cmd = self._calls.pop()
            cmd = last_called_cmd.cmd

        try:
            cmd.execute(self.env)
        except FunctionCalled:
            self._calls.append(CallingCommand(caller_addr, cmd))
        except InputCalled:
            self._inputcmd = cmd
            return RuntimeResult.PAUSED
        except:
            raise

        if isinstance(cmd, End):
            return RuntimeResult.TERMINATED

        self.env.update_addr_to_next_command()
        next_line = self.env.code[self.env.addr.line]
        kwd = Keyword(next_line[Index.KEYWORD])
        while kwd in (Keyword.COMMENT, Keyword.IFS):
            cmd = self.parser.read(next_line)
            cmd.execute(self.env)
            self.env.update_addr_to_next_command()
            next_line = self.env.code[self.env.addr.line]
            kwd = Keyword(next_line[Index.KEYWORD])

        if self.env.addr.line in self.breakpoints:
            return RuntimeResult.BREAKPOINT

        return RuntimeResult.EXECUTED


class CallingCommand:
    def __init__(self, addr: Address, cmd: Command):
        self.addr = addr
        self.cmd = cmd
