import os
import typing as tp

from operations.operation_registry import register_operation

from .common_parsers.tsv_parser import parse_tsv_to_str_cols, save_cols_to_tsv


@register_operation
class TsvFilterColumnsOperation:
    """
    TsvFilterColumnsOperation renames columns in tsv-file
    params:
        input_filename
        output_filename
        column_whitelist: list of column names to keep
        column_blacklist: list of column names to delete
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.column_whitelist = []
        self.column_blacklist = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'TsvFilterColumnsOperation':
        op = TsvFilterColumnsOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.column_whitelist = section.get('column_whitelist', [])
        op.column_blacklist = section.get('column_blacklist', [])
        assert op.column_whitelist or op.column_blacklist, "both column_whitelist and column_blacklist are empty"
        assert set(op.column_whitelist) & set(op.column_blacklist) == set(), "column_whitelist and column_blacklist have common keys"
        return op

    def run(self) -> None:
        column_name_to_column = parse_tsv_to_str_cols(self.input_filename)
        column_name_to_column = {
            column_name: column
            for column_name, column in column_name_to_column.items()
            if column_name in self.column_whitelist and column_name not in self.column_blacklist
        }

        save_cols_to_tsv(self.output_filename, column_name_to_column)
