import typing
from ..environment import Environment
import abc
from ..error import (
    OutOfRangeError,
    KeyNotContainedError,
    AssignmentNotSupportedError,
)


class Assignable(abc.ABC):
    @abc.abstractmethod
    def assign(self, value: typing.Any, env: Environment) -> None:
        pass

    @abc.abstractmethod
    def evaluate(self, env: Environment) -> typing.Any:
        pass


class Variable(Assignable):
    def __init__(self, name: str) -> None:
        self.name = name

    def assign(self, value: typing.Any, env: Environment) -> None:
        env.context.define(self.name, value)

    def evaluate(self, env: Environment) -> typing.Any:
        return env.context.lookup(self.name)

    def __str__(self) -> str:
        return self.name


class Attribute(Assignable):
    def __init__(
        self, obj: typing.Union[str, Assignable], properties: list[str]
    ) -> None:
        self.obj = obj
        self.properties = properties

    def assign(self, value: typing.Any, env: Environment) -> None:
        target = self._lookup(env)
        for prop in self.properties[:-1]:
            target = getattr(target, prop)
        setattr(target, self.properties[-1], value)

    def evaluate(self, env: Environment) -> typing.Any:
        target = self._lookup(env)
        for prop in self.properties:
            target = getattr(target, prop)
        return target

    def _lookup(self, env: Environment) -> typing.Any:
        if isinstance(self.obj, Assignable):
            return self.obj.evaluate(env)
        return self.obj

    def __str__(self) -> str:
        return f'{self.obj}.{".".join(self.properties)}'


KeyType = typing.Union[int, str, Assignable]
KeyIndex = typing.Union[int, Variable]


class Subscript(Assignable):
    def __init__(
        self,
        ref: Assignable,
        key: typing.Optional[KeyType],
        start: typing.Optional[KeyIndex] = None,
        stop: typing.Optional[KeyIndex] = None,
    ) -> None:
        self.ref = ref
        self.key = key
        self.start = start
        self.stop = stop

    def assign(self, value: typing.Any, env: Environment) -> None:
        obj: typing.Any = self.ref.evaluate(env)
        key: typing.Any = env.evaluate(self.key)
        start: typing.Optional[int] = env.evaluate(self.start)
        stop: typing.Optional[int] = env.evaluate(self.stop)

        if key is not None:
            try:
                obj[key] = value
                return
            except IndexError:
                raise OutOfRangeError(str(self.ref), str(key))
            except TypeError:
                raise AssignmentNotSupportedError(str(self.ref))
        if start is None:
            if stop is None:
                obj[:] = value
                return
            else:
                obj[:stop] = value
                return
        else:
            if stop is None:
                obj[start:] = value
                return
            else:
                obj[start:stop] = value
                return

    def evaluate(self, env: Environment) -> typing.Any:
        obj: typing.Any = self.ref.evaluate(env)
        key: typing.Any = env.evaluate(self.key)
        start: typing.Optional[int] = env.evaluate(self.start)
        stop: typing.Optional[int] = env.evaluate(self.stop)

        if key is not None:
            try:
                return obj[key]
            except IndexError:
                raise OutOfRangeError(str(self.ref), str(key))
            except KeyError:
                raise KeyNotContainedError(str(self.ref), str(key))
        if start is None:
            if stop is None:
                return obj[:]
            else:
                return obj[:stop]
        else:
            if stop is None:
                return obj[start:]
            else:
                return obj[start:stop]

    def __str__(self) -> str:
        return f"{self.ref}[{self.key}]"
