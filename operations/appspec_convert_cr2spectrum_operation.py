import json
import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation

from .lsrm_parsers.speparser import Spectrum, SpectrumInformation, save_spectrum_as_txt


def _read_appspec(filename: str) -> np.ndarray:
    with open(filename) as f:
        return np.array([float(line.rstrip()) for line in f if line.rstrip()])


def _read_calculation_time(filename: str) -> float:
    with open(filename) as f:
        data = json.load(f)
    return data["CalculationResults"]["calculation_time"]


def create_spectrum(appspec_filename: str, physspec_filename: str, output_filename: str):
    count_rates = _read_appspec(appspec_filename)
    calculation_time = _read_calculation_time(physspec_filename)
    spectrum_data = (count_rates * calculation_time).astype(np.int32)

    spectrum = Spectrum(
        spectrum_data,
        SpectrumInformation(tlive=calculation_time, treal=calculation_time))
    save_spectrum_as_txt(spectrum, output_filename)


@register_operation
class AppspecConvertcr2spectrumOpertation:
    """
    AppspecConvertcr2spectrumOpertation calculates app.spectrum from physspec using appspec.dll(.so)
    parameters:
        - input_appspec_spectrum_filename: appspec output filename with spectrum (count-rates)
        - input_physspec_out_filename: physspec_output filename with calculation time
        - output_filename: filename for output spectrum
    """
    def __init__(self):
        self.input_appspec_spectrum_filename = "appspec_input.json"
        self.input_physspec_out_filename = "physspec_output.json"
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'AppspecConvertcr2spectrumOpertation':
        op = AppspecConvertcr2spectrumOpertation()
        op.input_appspec_spectrum_filename = os.path.join(
            project_dir,
            section.get('input_appspec_spectrum_filename', op.input_appspec_spectrum_filename))
        op.input_physspec_out_filename = os.path.join(
            project_dir,
            section.get('input_physspec_out_filename', op.input_physspec_out_filename))
        op.output_filename = os.path.join(project_dir,
                                          section.get('output_filename', op.output_filename))
        return op

    def run(self) -> None:
        print('start appspec_convertcr2spectrum operation')
        create_spectrum(
            self.input_appspec_spectrum_filename,
            self.input_physspec_out_filename,
            self.output_filename)
