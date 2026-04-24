import json
import os
import typing as tp

from operations.operation_registry import register_operation


def _merge_jsonfiles(infile_names: tp.List[str], outfile_name: str, to_indent_output: bool):
    res  = {}
    for input_filename in infile_names:
        with open(input_filename, 'r') as f:
            data = json.load(f)
            res |= data
    with open(outfile_name, 'w') as g:
        indent = 4 if to_indent_output else None
        json.dump(res, g, indent=indent)


def _add_prefix_to_filenames(dir_name: str, filenames: tp.List[str]) -> tp.List[str]:
    return [os.path.join(dir_name, name) for name in filenames]


@register_operation
class JsonMergeFilesOperation:
    """
    JsonMergeFilesOperation edits json-files used for calculation modules
    parameters:
        - input_filenames: array of input json-filename
        - output_filename: merged output json-filename, can be same as input_filename
        - to_indent_output: use spaces and CR in output file or create one-line json
    """
    def __init__(self):
        self.input_filenames = []
        self.output_filename = ""
        self.to_indent_output = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'JsonMergeFilesOperation':
        op = JsonMergeFilesOperation()
        op.input_filenames = _add_prefix_to_filenames(project_dir, section['input_filenames'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.to_indent_output = section.get('to_indent_output', op.to_indent_output)
        assert op.input_filenames
        return op

    def run(self) -> None:
        print('start json_merge_files operation')
        _merge_jsonfiles(self.input_filenames, self.output_filename, self.to_indent_output)
