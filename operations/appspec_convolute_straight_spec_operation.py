import json
import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation
from .lsrm_parsers.speparser import Spectrum, SpectrumInformation, save_spectrum_as_txt
from .mcmodules_wrappers.appspec_wrapper import AppspecDllWrapper

APPSPEC_NAME = "test_spe.json"


def _convolute_spectr(physspec_output_filename: str):
    appspec_dll = AppspecDllWrapper()
    res = appspec_dll.make_apparatus_spectrum(physspec_output_filename, "test_spe.json")
    if res != 0:
        raise Exception(f"Error in making app spectrum: {res}")


def _read_spe_from_json(spe_name: str) -> tp.Tuple[np.ndarray, float]:
    with open(spe_name) as f:
        spe_dict = json.load(f)

    live_time = spe_dict["ApparatusSpectrum"]["live_time"]
    spe_data = spe_dict["ApparatusSpectrum"]["data"]
    return np.array(spe_data), live_time


def _save_spectrum_spe(spe_output_filename: str):
    spe_data, live_time = _read_spe_from_json(APPSPEC_NAME)
    spe_info = SpectrumInformation(
        name="AppSpec",
        tlive=live_time, treal=live_time,
        # geometry=..., distance=..., headerdict=...,
    )
    spe = Spectrum(spe_data, spe_info)
    save_spectrum_as_txt(spe, spe_output_filename, save_additional_params=True)


@register_operation
class AppspecConvoluteStraightSpecOperation:
    """
    AppspecConvoluteStraightSpecOperation runs appspec on physspec output json-file and makes spectrum
    """
    def __init__(self):
        self.physspec_output_filename = ""
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'AppspecConvoluteStraightSpecOperation':
        op = AppspecConvoluteStraightSpecOperation()
        op.physspec_output_filename = os.path.join(project_dir, section['physspec_output_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        return op

    def run(self) -> None:
        print('start appspec_convolute_straight_spectrum operation')
        _convolute_spectr(self.physspec_output_filename)
        _save_spectrum_spe(self.output_filename)
