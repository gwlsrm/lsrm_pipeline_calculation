import os
import typing as tp

from operations.operation_registry import register_operation


def _edit_infile(infile_name: str, outfile_name: str, params: tp.Dict[str, tp.Any]):
    with open(infile_name, 'r') as f, open(outfile_name, 'w') as g:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//') or '=' not in line:
                g.write(line + '\n')
                continue
            key, _ = [w.strip() for w in line.split('=', maxsplit=1)]
            if key in params:
                line = f'{key} = {params[key]}'
            g.write(line + '\n')


@register_operation
class EditInFileOperation:
    """
    EditInFileOperation edits in-files for tccfcalc calculation
    parameters:
        - input_filename: input in-file for tccfcalc calculation
        - output_filename: desirable output in-file name, must differ from input_filename
        - edit_params: list with name and value: [{name: param_name, value: param_value}, ...]
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.edit_params = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EditInFileOperation':
        op = EditInFileOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        assert op.input_filename != op.output_filename, \
            "same filenames are not supported in EditInFileOperation"
        op.edit_params = section.get('edit_params', op.edit_params)
        return op

    def run(self) -> None:
        print('start edit_infile_params')
        params = {r['name']: r['value'] for r in self.edit_params}
        _edit_infile(self.input_filename, self.output_filename, params)
