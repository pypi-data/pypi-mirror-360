class BaseCalciumError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class AssignmentNotSupportedError(BaseCalciumError):
    def __init__(self, obj: str):
        super().__init__(f"cannot assign to {obj}")
        self.obj = obj


class InvalidBreakError(BaseCalciumError):
    def __init__(self):
        super().__init__("break statement not within loop")


class InvalidContinueError(BaseCalciumError):
    def __init__(self):
        super().__init__("continue statement not within loop")


class InvalidModuleNameError(BaseCalciumError):
    def __init__(self, name: str):
        super().__init__(f"module name {name} is invalid")
        self.name = name


class InvalidReturnError(BaseCalciumError):
    def __init__(self):
        super().__init__("return statement not within function")


class KeyNotContainedError(BaseCalciumError):
    def __init__(self, obj: str, key: str):
        super().__init__(f"key {key.replace('\n', '\\n')} not contained in {obj}")
        self.obj = obj
        self.key = key


class NameNotFoundError(BaseCalciumError):
    def __init__(self, name: str):
        super().__init__(f"Name {name} is not defined")
        self.name = name


class ObjectNotCallableError(BaseCalciumError):
    def __init__(self, obj: str):
        super().__init__(f"object {obj} is not callable")
        self.obj = obj


class ObjectNotIterableError(BaseCalciumError):
    def __init__(self, obj: str):
        super().__init__(f"object {obj} is not iterable")
        self.obj = obj


class OperatorNotSupportedError(BaseCalciumError):
    def __init__(self, op: str):
        super().__init__(f"operator {op} not supported")
        self.op = op


class OutOfRangeError(BaseCalciumError):
    def __init__(self, obj: str, index: str):
        super().__init__(f"index out of range in {obj} at {index}")
        self.obj = obj
        self.index = index
