import json
import os
import typing as tp

from operations.operation_registry import register_operation


def _merge_json_files(input_filenames: tp.List[str], output_filename: str, to_indent: bool):
    data = {}
    for input_filename in input_filenames:
        with open(input_filename) as f:
            data |= json.load(f)

    indent = 4 if to_indent else None
    with open(output_filename, 'w') as g:
        json.dump(data, g, indent=indent)


@register_operation
class MergeJsons:
    """
    MergeJsons merge all json files to one
    parameters:
        input_filenames: list of json filenames to merge
        output_filename: desirable output json-filename
        pretty_json: add indents to output json
    """
    def __init__(self):
        self.input_filenames: tp.List[str] = []
        self.output_filename: str = ""
        self.indent = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'MergeJsons':
        op = MergeJsons()
        op.input_filenames = [
            os.path.join(project_dir, input_filename)
            for input_filename in section['input_filenames']]
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.indent = section.get("pretty_json", False)
        return op

    def run(self) -> None:
        print('start merge json-files')
        _merge_json_files(self.input_filenames, self.output_filename, self.indent)
