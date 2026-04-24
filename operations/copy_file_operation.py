import os
import shutil
import typing as tp

from operations.operation_registry import register_operation


@register_operation
class CopyFileOperation:
    """
    CopyFileOperation copies file from source to target location
    parameters:
        - input_filename: input in-file for tccfcalc calculation
        - output_filename: desirable output in-file name, must differ from input_filename
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'CopyFileOperation':
        op = CopyFileOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        assert op.input_filename != op.output_filename, \
            "CopyFileOperation: copy file to itself is pointless"
        return op

    def run(self) -> None:
        print('start copy_file operation')
        shutil.copyfile(self.input_filename, self.output_filename)
