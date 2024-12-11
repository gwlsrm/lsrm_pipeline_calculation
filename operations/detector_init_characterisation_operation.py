import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation
from .common_parsers.tsv_parser import parse_tsv_to_float_cols


DETECTOR_TYPE_TO_PARAM_NAMES = {
    "COAXIAL": ["DC_CrystalDiameter", "DC_CrystalHeight", "DC_CrystalFrontDeadLayer", "DC_CrystalSideDeadLayer"]
}


def _load_eff_from_tsv(filename: str) -> tp.Optional[tp.List[float]]:
    values = parse_tsv_to_float_cols(filename)
    return values.get("efficiency") or values.get("Eff")


def _edit_infile(infile_name: str, outfile_name: str, params: tp.Dict[str, tp.Any]):
    with open(infile_name, 'r') as f, open(outfile_name, 'w') as g:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//') or '=' not in line:
                g.write(line + '\n')
                continue
            key, _ = [w.strip() for w in line.split('=', maxsplit=1)]
            if key in params:
                line = f'{key} = {params[key]}'
            g.write(line + '\n')


def _minimize_det_parameters(tsv_filename: str, matrix_file: str, infile: str, detector_type: str
                             ) -> tp.List[float]:
    eff = _load_eff_from_tsv(tsv_filename)
    assert eff
    a = np.load(matrix_file)
    y = np.log(eff) - a[0, :]
    b = a[1:, :]
    x_hat, _, _, _ = np.linalg.lstsq(b.T, y, rcond=None)
    d = np.exp(x_hat[0])
    h = x_hat[1]**2
    dl = x_hat[2]
    d += 2*dl
    h += dl
    return [d, h, dl, dl]


@register_operation
class DetectorInitCharacterisationOperation:
    """
    DetectorInitCharacterisationOperation makes the 1st step in detector characterisation
    It optimizes detector parameters from precalculated coefficients.
    The precalculated coeffs depend on detector material and to point distance
    parameters:
        - input_in_filename: with initial detector params values
        - input_tsv_filename: input tsv-file with efficiency
        - input_matrix_file: input npy-file with precalculated coefficients for characterisation
        - output_filename: desirable output in-file name with fitted detector diameter, height
            and frontal thick
    """
    def __init__(self):
        self.input_in_filename = ""
        self.input_tsv_filename = ""
        self.input_matrix_file = ""
        self.output_filename = ""
        self.detector_type = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str
                        ) -> 'DetectorInitCharacterisationOperation':
        op = DetectorInitCharacterisationOperation()
        op.input_in_filename = os.path.join(project_dir, section['input_in_filename'])
        op.input_tsv_filename = os.path.join(project_dir, section['input_tsv_filename'])
        op.input_matrix_file = os.path.join(project_dir, section['input_matrix_file'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.detector_type = section["detector_type"]
        assert op.input_in_filename != op.output_filename, "input and output in-files cannot be the same"
        assert op.detector_type in DETECTOR_TYPE_TO_PARAM_NAMES, "unsupported detector type"
        return op

    def run(self) -> None:
        print('start detector_init_characterisation operation')

        param_values = _minimize_det_parameters(self.input_tsv_filename, self.input_matrix_file,
                                          self.input_in_filename, self.detector_type)
        param_names = DETECTOR_TYPE_TO_PARAM_NAMES[self.detector_type]
        params = {n: v for n, v in zip(param_names, param_values)}
        _edit_infile(self.input_in_filename, self.output_filename, params)
