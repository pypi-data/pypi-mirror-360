from .command import Command
from ..environment import Environment
from ..error import InvalidModuleNameError


class Import(Command):
    def __init__(self, path: str):
        self.path = path

    def execute(self, env: Environment) -> None:
        module_names = self.path.split(".")
        for name in module_names:
            if not name.isalnum():
                raise InvalidModuleNameError(name)
        exec(f"import {self.path}")
        module_name = module_names[0]
        env.context.define(module_name, eval(module_name))
