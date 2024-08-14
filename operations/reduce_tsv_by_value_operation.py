import math
import os
import typing as tp

from operations.operation_registry import register_operation


def _read_header(input_filename: str) -> tp.List[str]:
    with open(input_filename) as f:
        for line in f:
            return [w for w in line.strip().split('\t')]


def _read_row(input_filename: str, pivot_value: float) -> tp.List[float]:
    with open(input_filename) as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            line = line.strip()
            data = [float(w) for w in line.split('\t')]
            if math.isclose(data[0], pivot_value):
                return data


def _reduce_tsv_by_value(input_filenames: tp.List[str], output_filename: str,
                         new_axis_name: str, new_axes_values: tp.List[float],
                         pivot_value: float):
    header = [new_axis_name] + _read_header(input_filenames[0])
    new_data = []
    for input_filename, new_value in zip(input_filenames, new_axes_values):
        new_data.append([new_value] + _read_row(input_filename, pivot_value))

    # save new data to output
    with open(output_filename, 'w') as f:
        f.write("\t".join(header))
        f.write("\n")
        for row in new_data:
            f.write("\t".join([str(v) for v in row]))
            f.write("\n")


@register_operation
class ReduceTsvByValueOperation:
    """
    ReduceTsvByValueOperation reduce bunch of tsv by value
    """
    def __init__(self):
        self.input_filenames = []
        self.output_filename = ""
        self.new_axis_name = "name"
        self.new_axis_values = []
        self.col1value_pivot = 0.0

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'ReduceTsvByValueOperation'):
        op = ReduceTsvByValueOperation()
        op.input_filenames = [
            os.path.join(project_dir, input_filename)
            for input_filename in section['input_filenames']]
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.new_axis_name = section["new_axis_name"]
        op.new_axis_values = section["new_axis_values"]
        assert len(op.input_filenames) == len(op.new_axis_values)
        op.col1value_pivot = section.get('col1value_pivot', op.col1value_pivot)
        return op

    def run(self) -> None:
        print('start reduce_tsv_by_value')
        _reduce_tsv_by_value(self.input_filenames, self.output_filename,
                             self.new_axis_name, self.new_axis_values,
                             self.col1value_pivot)
