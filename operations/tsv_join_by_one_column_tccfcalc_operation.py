import os
import typing as tp

from operations.operation_registry import register_operation


def _parse_tsv_column_format(filename: str) -> tp.Dict[str, tp.List[float]]:
    with open(filename) as f:
        header = None
        data = {}
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            # read header
            if not header:
                header = line.split('\t')
                continue

            # read data
            d = [float(t) for t in line.split('\t')]
            for n, v in zip(header, d):
                data.setdefault(n, [])
                data[n].append(v)
    return data


def _add_to_tsv(output_filename: str, row_exist_values: tp.List[tp.Any],
                col: tp.List[float]):
    with open(output_filename, 'a') as f:
        f.write('\t'.join([str(v) for v in row_exist_values + col]))
        f.write('\n')


@register_operation
class TsvOneColumnJoinOperation:
    """
    TsvOneColumnJoinOperation makes dataset for detector characterisation from tsv-files
        (effcalc converted calculatoin results). It takes input file content, makes
        a row and appends to output tsv-file.
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.column_name = "Eff"
        self.row_exist_values = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'TsvOneColumnJoinOperation':
        op = TsvOneColumnJoinOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.column_name = section.get("column_name", op.column_name)
        op.row_exist_values = section.get("row_exist_values", op.row_exist_values)
        return op

    def run(self) -> None:
        print('start tsv_one_column_join operation')
        data = _parse_tsv_column_format(self.input_filename)
        _add_to_tsv(self.output_filename, self.row_exist_values, data[self.column_name])
