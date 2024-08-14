import typing as tp

from operations.operaton_interface import Operation


class _Register:
    def __init__(self) -> None:
        self.registry: tp.Dict[str, Operation] = {}

    def __call__(self, original_class):
        self.registry[original_class.__name__] = original_class
        return original_class


register_operation = _Register()
