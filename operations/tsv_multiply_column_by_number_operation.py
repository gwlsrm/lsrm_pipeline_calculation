import os
import typing as tp

from operations.operation_registry import register_operation

from .common_parsers.tsv_parser import parse_tsv_to_cols, save_cols_to_tsv


@register_operation
class TsvMultiplyColumnByNumberOperation:
    """
    TsvMultiplyColumnByNumberOperation multiply column by number
    params:
        input_filename
        output_filename
        column_name
        number
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.column_name = ""
        self.number = 0

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'TsvMultiplyColumnByNumberOperation':
        op = TsvMultiplyColumnByNumberOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.column_name = section['column_name']
        op.number = section['number']
        assert op.column_name
        return op

    def run(self) -> None:
        column_name_to_column = parse_tsv_to_cols(self.input_filename)
        column_name_to_column[self.column_name] = [x * self.number for x in column_name_to_column[self.column_name]]

        save_cols_to_tsv(self.output_filename, column_name_to_column)
