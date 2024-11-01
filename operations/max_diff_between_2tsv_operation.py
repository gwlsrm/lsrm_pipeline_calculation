import os
import typing as tp

from operations.operation_registry import register_operation

EPS = 1e-16


def _parse_tsv_output(filename: str) -> tp.Dict[str, tp.List[float]]:
    header_names = None
    res: tp.Dict[str, tp.List[float]] = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if header_names is None:
                header_names = [w for w in line.split('\t')]
                continue
            tokens = [float(w) for w in line.split('\t')]
            assert len(tokens) == len(header_names)
            for name, value in zip(header_names, tokens):
                res.setdefault(name, [])
                res[name].append(value)
    return res


def _calc_max_diff(input_filename_1: str, input_filename_2: str, column_name: str,
                   is_relative_diff: bool, relative_to_average: bool, output_filename: str):
    data_1 = _parse_tsv_output(input_filename_1)[column_name]
    data_2 = _parse_tsv_output(input_filename_2)[column_name]
    assert len(data_1) == len(data_2)
    max_diff = 0.0
    for left, right in zip(data_1, data_2):
        diff = abs(left - right)
        if is_relative_diff:
            base = (left + right) / 2 if relative_to_average else left
            diff = diff / (base + EPS)
        max_diff = max(max_diff, diff)

    with open(output_filename, 'w') as f:
        f.write(f'{max_diff}\n')


@register_operation
class CalcMaxDiffBetweenTwoColumns:
    """
    CalcMaxDiffBetweenTwoColumns calculates max diff between 2 columns in 2 tsv-files
    parameters:
        - input_filename_*: input tsv-file
        - column_name: column name in both files, values must be numerical
        - output_filename: output filename, where there will be maximum difference (one number)
        - is_relative_diff: relative difference to average of two values
            (if relative_to_average is set) or to the first value
    """
    def __init__(self):
        self.input_filename_1: str = ""
        self.input_filename_2: str = ""
        self.column_name: str = ""
        self.output_filename = ""
        self.is_relative_diff: bool = True
        self.relative_to_average = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'CalcMaxDiffBetweenTwoColumns'):
        op = CalcMaxDiffBetweenTwoColumns()
        op.input_filename_1 = os.path.join(project_dir, section['input_filename_1'])
        op.input_filename_2 = os.path.join(project_dir, section['input_filename_2'])
        op.column_name = section["column_name"]
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.is_relative_diff = section.get("is_relative_diff", True)
        op.relative_to_average = section.get("relative_to_average", False)
        return op

    def run(self) -> None:
        print('start calc max difference')
        _calc_max_diff(self.input_filename_1, self.input_filename_2, self.column_name,
                       self.is_relative_diff, self.relative_to_average,
                       self.output_filename)
