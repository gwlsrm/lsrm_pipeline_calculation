import os
import typing as tp

from operations.operation_registry import register_operation


def _merge_files(input_filenames: tp.List[str], output_filename: str, write_filename: bool):
    with open(output_filename, 'w') as g:
        for input_filename in input_filenames:
            if write_filename:
                g.write(f"{input_filename}: ")
            with open(input_filename) as f:
                for line in f:
                    g.write(line)


@register_operation
class MergeFilesOperation:
    """
    MergeFilesOperation merge all text files to one
    """
    def __init__(self):
        self.input_filenames: tp.List[str] = []
        self.output_filename: str = ""
        self.write_filename: bool = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'MergeFilesOperation':
        op = MergeFilesOperation()
        op.input_filenames = [
            os.path.join(project_dir, input_filename)
            for input_filename in section['input_filenames']]
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.write_filename = section.get("write_filename", False)
        return op

    def run(self) -> None:
        print('start merge files')
        _merge_files(self.input_filenames, self.output_filename, self.write_filename)
