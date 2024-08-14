import os
import shutil
import typing as tp

from operations.operation_registry import register_operation
from .mcmodules_wrappers.effcalc import calculate_eff
from .mcmodules_wrappers.nuclide import Nuclide


@register_operation
class EffCalcOperation:
    """
    EffcalcOperation calculates efficiency/tcc/spectrum using tccfcalc.dll
    """
    def __init__(self):
        self.input_filename = "tccfcalc.in"
        self.output_filename = "tccfcalc.out"
        self.histories = 1000
        self.nuclide: Nuclide = Nuclide.get_default()
        self.seed = 0
        self.activity = 1000.0

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EffCalcOperation':
        op = EffCalcOperation()
        op.input_filename = os.path.join(project_dir,
                                         section.get('input_filename', op.input_filename))
        op.output_filename = os.path.join(project_dir,
                                          section.get('output_filename', op.output_filename))
        op.histories = section.get('histories', op.histories)
        nuclide_str = section.get('nuclide', '')
        if nuclide_str:
            op.nuclide = Nuclide.parse_from(nuclide_str)
        op.seed = section.get('seed', op.seed)
        op.activity = section.get('activity', op.activity)
        return op

    def run(self) -> None:
        print('start effcalc')
        # copy input -> tccfcalc.in
        shutil.copy(self.input_filename, 'tccfcalc.in')
        # run effcalc
        calculate_eff(self.nuclide, self.histories, False, self.seed, self.activity)
        # copy tccfcalc.out -> output
        shutil.copy('tccfcalc.out', self.output_filename)
