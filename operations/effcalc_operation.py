import os
import shutil
import typing as tp

from operations.operation_registry import register_operation
from .mcmodules_wrappers.effcalc import calculate_eff, calculate_eff_json
from .mcmodules_wrappers.nuclide import Nuclide


@register_operation
class EffCalcOperation:
    """
    EffcalcOperation calculates efficiency/tcc/spectrum using tccfcalc.dll
    parameters:
        - input_filename: in-file
        - output_filename: out-file
        - histories: number of simulated histories in thousands
        - nuclide: nuclide in format: Co-60, default is gread (290.enx)
        - seed: seed for random generator, 0 -- random seed, >0 -- fixed seed
        - activity: activiy in Bq
        - batch_size: number of histories is splitted on batches with size=batch-size.
            It's used only for logging steps. -1 -- batchsize = histories
    """
    def __init__(self):
        self.input_filename = "tccfcalc.in"
        self.output_filename = "tccfcalc.out"
        self.histories = 1000
        self.nuclide: Nuclide = Nuclide.get_default()
        self.seed = 0
        self.activity = 1000.0
        self.is_calc_spectrum = False
        self.output_spe_name = "test_spectr.spe"
        self.batch_size = -1

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
        op.is_calc_spectrum = section.get('is_calc_spectrum', op.is_calc_spectrum)
        op.output_spe_name = os.path.join(project_dir,
                                          section.get('output_spe_name', op.output_spe_name))
        op.batch_size = section.get('batch_size', op.histories
                                    if op.batch_size < 0 else op.batch_size)
        return op

    def run(self) -> None:
        print('start effcalc')
        # run effcalc
        if self.input_filename.endswith(".in"):
            shutil.copy(self.input_filename, 'tccfcalc.in')
            calculate_eff(self.nuclide, self.histories, self.is_calc_spectrum, self.seed, self.activity)
        elif self.input_filename.endswith(".json"):
            shutil.copy(self.input_filename, 'tccfcalc_input.json')
            calculate_eff_json(self.histories, self.is_calc_spectrum, self.seed, self.activity)
        else:
            raise Exception("unknown input file extension")
        # copy tccfcalc.out -> output
        shutil.copy('tccfcalc.out', self.output_filename)
        if self.is_calc_spectrum:
            shutil.copy('test_spectr.spe', self.output_spe_name)
