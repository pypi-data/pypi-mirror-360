import typing
from .error import NameNotFoundError


class Namespace:
    def __init__(
        self,
        parent: typing.Union["Namespace", None],
        dictobj: dict[str, typing.Any],
    ) -> None:
        self.parent = parent  # global scope has no parent
        self.dictobj = dictobj

    def define(self, name: str, value: typing.Any) -> None:
        self.dictobj[name] = value

    def lookup(self, name: str) -> typing.Any:
        try:
            return self.dictobj[name]
        except KeyError:
            if self.parent is None:
                raise NameNotFoundError(name)
            else:
                return self.parent.lookup(name)

    def find_nesting_scope(self) -> "Namespace":
        scope: Namespace = self
        while isinstance(scope, ClassScope):
            scope = scope.parent  # type: ignore
        return scope


class ClassScope(Namespace):
    def create_attributes(self) -> dict[str, typing.Any]:
        return self.dictobj


class FuncScope(Namespace):
    pass


class GlobalScope(Namespace):
    def lookup(self, name: str) -> typing.Any:
        try:
            return super().lookup(name)
        except:
            try:
                if isinstance(__builtins__, dict):
                    return __builtins__[name]
                else:
                    return getattr(__builtins__, name)
            except KeyError:
                raise NameNotFoundError(name)
            except:
                raise
