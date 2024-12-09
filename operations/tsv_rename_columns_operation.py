import os
import typing as tp

from operations.operation_registry import register_operation

from .common_parsers.tsv_parser import parse_tsv_to_str_rows, save_rows_to_tsv


def _rename_header(header: tp.List[str], columns_from: tp.List[str], columns_to: tp.List[str]
                   ) -> tp.List[str]:
    columns_from_to = {f: t for f, t in zip(columns_from, columns_to)}
    new_header = []
    for name in header:
        new_header.append(
            columns_from_to[name]
            if name in columns_from_to else
            name
        )
    return new_header


@register_operation
class TsvRenameColumnsOperation:
    """
    TsvRenameColumnsOperation renames columns in tsv-file
    params:
        input_filename
        output_filename
        columns_from: list of column names in inputfilename to renam
        columns_to: list of desired column names, must have the same length
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.columns_from = []
        self.columns_to = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'TsvRenameColumnsOperation':
        op = TsvRenameColumnsOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.columns_from = section.get('columns_from')
        op.columns_to = section.get('columns_to')
        assert op.columns_from and op.columns_to
        assert len(op.columns_from) == len(op.columns_to)
        return op

    def run(self) -> None:
        print('start tsv_rename_columns operation')
        header, rows = parse_tsv_to_str_rows(self.input_filename)
        header = _rename_header(header, self.columns_from, self.columns_to)

        save_rows_to_tsv(self.output_filename, header, rows)
