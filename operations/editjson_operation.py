import json
import os
import typing as tp

from operations.operation_registry import register_operation


def _edit_jsonfile(infile_name: str, outfile_name: str, params: tp.Dict[str, tp.Any],
                   to_indent_output: bool):
    with open(infile_name, 'r') as f:
        data = json.load(f)
    for key, v in params.items():
        if '.' in key:
            key_fields = key.split('.')
        else:
            key_fields = [key]
        d = data
        for i, k in enumerate(key_fields):
            if i+1 != len(key_fields):
                d = d[k]
            else:
                d[k] = v
    with open(outfile_name, 'w') as g:
        indent = 4 if to_indent_output else None
        json.dump(data, g, indent=indent)


@register_operation
class EditJsonOperation:
    """
    EditJsonOperation edits json-files used for calculation modules
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.edit_params = []
        self.to_indent_output = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EditJsonOperation':
        op = EditJsonOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.edit_params = section.get('edit_params', op.edit_params)
        op.to_indent_output = section.get('to_indent_output', op.to_indent_output)
        return op

    def run(self) -> None:
        print('start edit_json_params')
        params = {r['name']: r['value'] for r in self.edit_params}
        _edit_jsonfile(self.input_filename, self.output_filename, params, self.to_indent_output)
