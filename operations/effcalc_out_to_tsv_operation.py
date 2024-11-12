import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers.out_file_parser import parse_out_file_row_format


def _save_tsv(header: tp.List[str], rows: tp.List[tp.List[float]], output_filename: str):
    with open(output_filename, 'w') as f:
        header_str = '\t'.join(header)
        f.write(header_str)
        f.write('\n')
        for row in rows:
            line = '\t'.join([str(v) for v in row])
            f.write(line)
            f.write('\n')


@register_operation
class EffCalcOutToTsvOperation:
    """
    EffCalcOutToTsvOperation converts effcalc output (out-file) to tsv-file
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EffCalcOutToTsvOperation':
        op = EffCalcOutToTsvOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        return op

    def run(self) -> None:
        print('start effcalc_out_to_tsv_operation')
        header, rows = parse_out_file_row_format(self.input_filename)
        _save_tsv(header, rows, self.output_filename)
