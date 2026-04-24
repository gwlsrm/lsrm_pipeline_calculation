import os
import shutil
import typing as tp

from operations.operation_registry import register_operation
from .mcmodules_wrappers.appspec import calc_spectrum


@register_operation
class AppspecSpectrumOperation:
    """
    AppspecSpectrumOperation calculates app.spectrum from physspec using appspec.dll(.so)
    parameters:
        - input_filename: appspec input filename for calculation
        - output_filename: desirable output filename
        - is_log: use log for approximation
    """
    def __init__(self):
        self.input_filename = "appspec_input.json"
        self.output_filename = "appspec_output.json"
        self.is_log = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'AppspecSpectrumOperation':
        op = AppspecSpectrumOperation()
        op.input_filename = os.path.join(project_dir,
                                         section.get('input_filename', op.input_filename))
        op.output_filename = os.path.join(project_dir,
                                          section.get('output_filename', op.output_filename))
        return op

    def run(self) -> None:
        print('start appspec_spectrum calculation')
        # calc efficiency
        calc_spectrum(self.input_filename, self.output_filename)
