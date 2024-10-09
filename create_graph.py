import os
import typing as tp
import yaml

from operations import register_operation
from operations import Operation


class Graph:
    def __init__(self, operations: tp.Optional[tp.List[Operation]] = None):
        self.operations = operations or []

    def run(self) -> None:
        for operation in self.operations:
            operation.run()


def parse_config(filename: str) -> Graph:
    project_dir = os.path.dirname(filename)
    with open(filename) as f:
        docs = yaml.safe_load(f)
        operations = []
        for operation_rec in docs:
            t = register_operation.registry[operation_rec['type']]
            operation = t.parse_from_yaml(operation_rec, project_dir)
            operations.append(operation)
    graph = Graph(operations)
    return graph
