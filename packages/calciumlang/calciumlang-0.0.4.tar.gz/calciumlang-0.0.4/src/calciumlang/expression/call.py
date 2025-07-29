from inspect import signature
import typing
from .assignable import Attribute, Variable
from ..command.class_stmt import Class
from ..command.function import Def
from ..environment import Environment
from ..error import ObjectNotCallableError
from ..label import InputCalled


class Call:
    def __init__(
        self,
        callee: typing.Union[Variable, Attribute],
        args: list[typing.Any],
    ) -> None:
        self.callee = callee
        self.args = args
        self.value: typing.Any = None
        self.is_called = False
        self.is_returned = False

    def evaluate(self, env: Environment) -> typing.Any:
        funcobj = self.callee.evaluate(env)
        kwargs = {
            arg.kwd: env.evaluate(arg.value)
            for arg in self.args
            if isinstance(arg, KeywordArgument)
        }
        evaluated_args = [
            env.evaluate(arg)
            for arg in self.args
            if not isinstance(arg, KeywordArgument)
        ]

        # built-in input() function requires the runtime to be paused
        if funcobj is input:
            if not self.is_called:
                self.is_called = True
                if len(evaluated_args) > 0:
                    env.prompt = evaluated_args[0]
                raise InputCalled()
            if not self.is_returned:
                self.is_returned = True
                self.value = env.returned_value
                env.prompt = ""
            return self.value
        if funcobj is super:
            if not self.is_called:
                this = env.context.lookup("self")
                klass = this.__class__
                self.is_called, self.is_returned = True, True
                self.value = super(klass, this)
            return self.value

        if not self.is_called:
            self.is_called = True
            if callable(funcobj) and funcobj.__module__ in (
                Class.__module__,
                Def.__module__,
            ):
                # user defined function
                sig = signature(funcobj)
                if "*args" in str(sig):
                    kwargs["is_called_by_library"] = False
            try:
                self.value = funcobj(*evaluated_args, **kwargs)
                self.is_returned = True  # built-ins also reach here
                return self.value
            except TypeError:
                raise ObjectNotCallableError(str(funcobj))
        if not self.is_returned:
            self.is_returned = True
            self.value = env.returned_value
            env.returned_value = None
        return self.value


class KeywordArgument:
    def __init__(self, kwd: str, value: typing.Any) -> None:
        self.kwd = kwd
        self.value = value
