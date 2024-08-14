import typing as tp
from abc import ABC, abstractmethod


class Operation(ABC):
    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'Operation':
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError


def update_field(field, section, name):
    if name in section:
        return section[name]
    else:
        return field
