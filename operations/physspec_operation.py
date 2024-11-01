import os
import shutil
import typing as tp

from operations.operation_registry import register_operation
from .mcmodules_wrappers.physspec import calc_physspec


@register_operation
class PhysspecOperation:
    """
    PhysspecOperation calculates physical spectrum using physspec.dll (physspec.so)
    """
    def __init__(self):
        self.input_filename = "physspec_input.json"
        self.output_filename = "physspec_output.json"
        self.histories = 1000
        self.seed = 0

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'PhysspecOperation':
        op = PhysspecOperation()
        op.input_filename = os.path.join(project_dir,
                                         section.get('input_filename', op.input_filename))
        op.output_filename = os.path.join(project_dir,
                                          section.get('output_filename', op.output_filename))
        op.histories = section.get('histories', op.histories)
        op.seed = section.get('seed', op.seed)
        return op

    def run(self) -> None:
        print('start physspec calculation')
        # copy input -> physspec_input.json
        if self.input_filename != 'physspec_input.json':
            shutil.copy(self.input_filename, 'physspec_input.json')
        # run physspec
        calc_physspec(self.seed, self.histories)
        # copy physspec_output.json -> output
        if self.output_filename != 'physspec_output.json':
            shutil.copy('physspec_output.json', self.output_filename)
