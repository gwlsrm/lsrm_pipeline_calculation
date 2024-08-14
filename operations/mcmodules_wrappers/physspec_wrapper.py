import os.path
import sys
import typing as tp
from ctypes import CDLL, RTLD_GLOBAL, POINTER, Structure, \
    c_int, c_bool, c_double, c_char_p


PREPARE_ERROR_CODES = [
    "",
    "Memory allocation error.",
    "Unable to load Photon Attenuation Library files.",
    "No GLECS database.",
    "Could not find ECCBINDX.BIN data file.",
    "TCCFCALC.IN file not found.",
    "Incorrect input geometry or material data",
    "No ENSDF data found for the specified A, Z and M.",
    "There is no valid record in ENSDF data library.",
    "ENSDF: Normalization record is not complete.",
    "Could not find ICC.BIN data file.",
    "No X- or gamma-rays are emitted by the source.",
    "No EPDL97 library",
    "No Ttb library",
    "No Elib library",
    "Bad input json file",
    "Error while parsing input json file",
]


class CalculationResults(Structure):
    _fields_ = [
        ('npeaks', c_int),
        ('y0', POINTER(c_double)),
        ('x1', POINTER(c_double)),
        ('y1', POINTER(c_double)),
        ('dy1', POINTER(c_double)),
        ('nchannels', c_int),
        ('x2', POINTER(c_double)),
        ('y2', POINTER(c_double)),
        ('fcol', c_double),
        ('dfcol', c_double),
    ]


def _get_attribute(lib, attributes: tp.List[str]):
    """
        tries to get exported attribute from attributes list
        returns first successful
    """
    for attribute in attributes:
        try:
            res = getattr(lib, attribute)
            return res
        except AttributeError:
            continue
    raise AttributeError('Cannot find good symbol from ' + str(attributes))


class PhysspecDllWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None):
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
        # prepare
        self._physspec_prepare = _get_attribute(self._lib,
                                                ['PhysSpecPrepareJson@8', 'PhysSpecPrepareJson'])
        self._physspec_prepare.argtypes = [c_char_p, c_int]
        # calculate
        self._physspec_calculate = _get_attribute(self._lib,
                                                  ['PhysSpec_Calculate@8', 'PhysSpec_Calculate'])
        self._physspec_calculate.argtypes = [c_int, c_bool]
        self._physspec_calculate.restype = POINTER(CalculationResults)
        # reset
        self._physspec_reset = _get_attribute(self._lib, ['PhysSpec_Reset@0', 'PhysSpec_Reset'])
        # save to json
        self._physspec_save_json = _get_attribute(self._lib,
                                                  ['PhysSpec_Save_Json@4', 'PhysSpec_Save_Json'])
        self._physspec_save_json.argtypes = [c_char_p]

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['physspec_p_gw.dll', 'libphysspec_p_gw.dll', 'libphysspec_p_gw.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find physspec library in "{path_to_dll}"')

    def physspec_prepare(self, input_filename: str, seed: int) -> int:
        return self._physspec_prepare(bytes(input_filename, 'utf-8'), seed)

    def physspec_calculate(self, histories: int, calculate_results: bool) -> CalculationResults:
        return self._physspec_calculate(histories, calculate_results)

    def physspec_reset(self) -> None:
        self._physspec_reset()

    def physspec_save_json(self, output_filename: str) -> None:
        self._physspec_save_json(bytes(output_filename, 'utf-8'))


def main():
    cur_path = os.getcwd()
    lib = PhysspecDllWrapper()

    # prepare
    input_filename = os.path.join(cur_path, 'physspec_input.json')
    error_num = lib.physspec_prepare(input_filename, 42)
    if error_num:
        error_msg = PREPARE_ERROR_CODES[error_num] if error_num < len(PREPARE_ERROR_CODES) else ''
        print(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()

    # calc
    res = lib.physspec_calculate(100000, True)
    if res != 0:
        print(f'Calculation error #{res}')

    # save
    output_filename = os.path.join(cur_path, 'physspec_output.json')
    lib.physspec_save_json(output_filename)

    print('done')


if __name__ == '__main__':
    main()
