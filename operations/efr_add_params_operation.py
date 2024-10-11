import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers import efaparser


def _save_output(eff: efaparser.Efficiency, output_filename: str):
    _, ext = os.path.splitext(output_filename)
    if ext == '.efr':
        eff.save_as_efr(output_filename)
    elif ext == '.efa':
        eff.save_as_efa(output_filename)
    else:
        raise RuntimeError("Unknown extension of output filename:", ext)


@register_operation
class EfrAddParametersOperation:
    """
    EfrAddParametersOperation converts efr-file to tsv-file (like appspec output)
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.parameters = {}

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str
                        ) -> 'EfrAddParametersOperation':
        op = EfrAddParametersOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir,
                                          section.get('output_filename', section['input_filename']))
        op.parameters = section["parameters"]
        return op

    def run(self) -> None:
        print('start efr_add_parameter')
        eff = efaparser.get_efficiency_from_efa(self.input_filename)
        for k, v in self.parameters.items():
            eff.header_lines.append((k, str(v)))
        _save_output(eff, self.output_filename)
