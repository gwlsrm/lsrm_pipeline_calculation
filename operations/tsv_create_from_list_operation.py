import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers.out_file_parser import parse_out_file_col_format


def _create_tsv(output_filename: str, row: tp.List[tp.Any]):
    with open(output_filename, 'w') as f:
        f.write('\t'.join([str(v) for v in row]))
        f.write('\n')


@register_operation
class TsvCreateFromList:
    """
    TsvCreateFromList creates file from list of values, it is useful for headers.
    """
    def __init__(self):
        self.output_filename = ""
        self.row = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'TsvCreateFromList':
        op = TsvCreateFromList()
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.row = section.get("row", op.row)
        return op

    def run(self) -> None:
        print('start tsv_create_from_list')
        _create_tsv(self.output_filename, self.row)
