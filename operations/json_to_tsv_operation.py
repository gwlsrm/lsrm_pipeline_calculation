import json
import os
import typing as tp

from operations.operation_registry import register_operation


def _get_list_size(d: tp.Dict[str, tp.List[tp.Any]]) -> int:
    n = None
    for _, arr in d.items():
        if n is None:
            n = len(arr)
        else:
            assert n == len(arr)
    return n


def _convert_json_to_tsv(infile_name: str, outfile_name: str, column_names: tp.List[str]):
    with open(infile_name, 'r') as f:
        data = json.load(f)

    res = {}
    for column_name in column_names:
        if '.' in column_name:
            key_fields = column_name.split('.')
        else:
            key_fields = [column_name]

        d = data
        for i, k in enumerate(key_fields):
            if i+1 != len(key_fields):
                d = d[k]
            else:
                res[column_name] = d[k]

    n = _get_list_size(res)

    with open(outfile_name, 'w') as g:
        g.write('\t'.join(column_names) + '\n')
        for i in range(n):
            for j, column_name in enumerate(column_names):
                g.write(str(res[column_name][i]))
                if j+1 == len(column_names):
                    g.write('\n')
                else:
                    g.write('\t')


@register_operation
class JsonToTsvOperation:
    """
    JsonToTsvOperation constructs tsv-file from json and fields. fields'll become column names.
    Fieds must be in format: token1.token2
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.column_names = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'JsonToTsvOperation':
        op = JsonToTsvOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.column_names = section.get('column_names', op.column_names)
        return op

    def run(self) -> None:
        print('start jsont_to_tsv')
        _convert_json_to_tsv(self.input_filename, self.output_filename, self.column_names)
