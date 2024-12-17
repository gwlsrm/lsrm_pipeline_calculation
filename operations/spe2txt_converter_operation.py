import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers.speparser import SpectrumReader, save_spectrum_as_txt


def _get_output_filename(input_filename: str) -> str:
    filename, _ = os.path.splitext(input_filename)
    return filename + '.txt'


@register_operation
class Spe2TxtOperation:
    """
    Spe2TxtOperation converts spe-file to txt-file
    parameters:
        input_filename: spe-filename
        output_filename: txt-filename, by default: input_name + '.txt'
        save_additional_fields: bool flag, convert all fields from spe to txt or only standard
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.save_additional_fields: bool = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'Spe2TxtOperation':
        op = Spe2TxtOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = section.get('output_filename')
        if not op.output_filename:
            op.output_filename = _get_output_filename(op.input_filename)
        else:
            op.output_filename = os.path.join(project_dir, op.output_filename)
        op.save_additional_fields = section.get("save_additional_fields", op.save_additional_fields)
        return op

    def run(self) -> None:
        print('start spe2txt_converter operation')
        print('converting:', self.input_filename)
        spectrum = SpectrumReader().parse_spe(self.input_filename)
        save_spectrum_as_txt(spectrum, self.output_filename, self.save_additional_fields)
