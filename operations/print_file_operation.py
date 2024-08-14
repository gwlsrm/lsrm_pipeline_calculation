import os
import typing as tp

from operations.operation_registry import register_operation


@register_operation
class PrintFileContent:
    """
    PrintFileContent prints file content
    """
    def __init__(self):
        self.input_filename: str = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'PrintFileContent':
        op = PrintFileContent()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        return op

    def run(self) -> None:
        print('start print file')
        with open(self.input_filename) as f:
            for line in f:
                print(line, end='')
