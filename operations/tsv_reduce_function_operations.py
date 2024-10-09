import csv
import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation


REDUCE_FUNCTIONS = {
    "min": np.argmin,
    "max": np.argmax,
}
REDUCE_FUNCTION_NAMES = list(REDUCE_FUNCTIONS.keys())


def _tsv_reduce_with_function(input_filename: str, output_filename: str, column_name: str,
                              func_name: str):
    header = {}
    col_idx = None
    data = []
    with open(input_filename) as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not header:
                header = {v: i for i, v in enumerate(row)}
                col_idx = header[column_name]
                continue
            data.append(row)

    column = np.array([float(row[col_idx]) for row in data])
    row_idx = REDUCE_FUNCTIONS[func_name](column)

    # save new data to output
    with open(output_filename, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerow(data[row_idx])


@register_operation
class TsvReduceFunctionOperation:
    """
    TsvReduceFunctionOperation reduce bunch of tsv by value
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.column_name = ""
        self.function = None

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'TsvReduceFunctionOperation'):
        op = TsvReduceFunctionOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.column_name = section["column_name"]
        op.function = section["function"]
        assert op.function in REDUCE_FUNCTION_NAMES
        return op

    def run(self) -> None:
        print('start tsv_reduce_with_function')
        _tsv_reduce_with_function(self.input_filename, self.output_filename,
                             self.column_name, self.function)
