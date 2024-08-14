import os
import shutil
import typing as tp

from operations.operation_registry import register_operation
from .mcmodules_wrappers.appspec import calc_efficiency


@register_operation
class AppspecOperation:
    """
    AppspecOperation calculates efficiency from physspec using appspec.dll
    """
    def __init__(self):
        self.input_filename = "appspec_input.json"
        self.output_filename = "appspec_output.json"
        self.is_log = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'AppspecOperation':
        op = AppspecOperation()
        op.input_filename = os.path.join(project_dir,
                                         section.get('input_filename', op.input_filename))
        op.output_filename = os.path.join(project_dir,
                                          section.get('output_filename', op.output_filename))
        op.is_log = section.get("is_log", op.is_log)
        return op

    def run(self) -> None:
        print('start appspec calculation')
        # copy input -> appspec_input.json
        if self.input_filename != 'appspec_input.json':
            shutil.copy(self.input_filename, 'appspec_input.json')
        # calc efficiency
        calc_efficiency('appspec_input.json', 'appspec_output.json', self.is_log)
        # copy appspec_output.json -> output
        if self.output_filename != 'appspec_output.json':
            shutil.copy('appspec_output.json', self.output_filename)
