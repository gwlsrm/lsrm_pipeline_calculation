import os.path
import sys
import typing as tp
import ctypes as ct

from .read_output_bin import convert_from_bin_to_txt


PREPARE_ERROR_CODES = [
    "",
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


class AppspecDllWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None):
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = ct.CDLL(os.path.join(path_to_dll, lib_name), ct.RTLD_GLOBAL)
        # efficiency
        # prepare
        self._prepare_efficiency_calculation = _get_attribute(
            self._lib,
            ['prepare_efficiency_calculation@20', 'prepare_efficiency_calculation']
        )
        self._prepare_efficiency_calculation.argtypes = [
            ct.c_int, ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double),
            ct.c_bool]
        # calculate
        self._calculate_efficiency = _get_attribute(self._lib, ['calculate_efficiency@40',
                                                                'calculate_efficiency'])
        self._calculate_efficiency.argtypes = [
            ct.c_double, ct.c_double, ct.c_double, ct.c_double, ct.POINTER(ct.c_double),
            ct.POINTER(ct.c_double)]
        self._calculate_efficiency.restype = ct.c_int
        # reset
        self._reset_efficiency_calculation = _get_attribute(
            self._lib,
            ['reset_efficiency_calculation@0', 'reset_efficiency_calculation']
        )
        # calculate efficiency using json-files
        self._calculate_efficiency_json = _get_attribute(self._lib, ['calculate_efficiency_json'])
        self._calculate_efficiency_json.argtypes = [
            ct.c_char_p, ct.c_char_p, ct.c_bool]
        self._calculate_efficiency_json.restype = ct.c_int
        # spectrum
        self._calc_apparatus_spectrum = _get_attribute(
            self._lib, ['calc_apparatus_spectrum@4', 'calc_apparatus_spectrum'])
        self._calc_apparatus_spectrum.argtypes = [ct.c_char_p]

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['appspec.dll', 'libappspec.dll', 'libappspec.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find appspec library in "{path_to_dll}"')

    def prepare_efficiency_calculation(self, energy_array: tp.List[float],
                                       nfep_array: tp.List[float], dfep_array: tp.List[float],
                                       is_log: bool) -> None:
        e = (ct.c_double * len(energy_array))(*energy_array)
        nfep = (ct.c_double * len(nfep_array))(*nfep_array)
        dfep = (ct.c_double * len(dfep_array))(*dfep_array)

        return self._prepare_efficiency_calculation(
            len(energy_array), e, nfep, dfep, is_log)

    def calculate_efficiency(self, energy: float, peak_count_rate: float, dpeak_count_rate: float,
                             peak_intensity: float) -> tp.Tuple[float, float, int]:
        efficiency = ct.c_double(-1.0)
        defficiency = ct.c_double(-1.0)
        error_num = self._calculate_efficiency(
            energy, peak_count_rate, dpeak_count_rate, peak_intensity,
            ct.pointer(efficiency), ct.pointer(defficiency))
        return efficiency, defficiency, error_num

    def reset_efficiency_calculation(self) -> None:
        self._reset_efficiency_calculation()

    def calc_apparatus_spectrum(self, input_filename: str) -> int:
        return self._calc_apparatus_spectrum(bytes(input_filename, 'utf-8'))

    def calculate_efficiency_json(self, input_filename: str, output_filename: str,
                                  is_log: bool) -> int:
        return self._calculate_efficiency_json(
            bytes(input_filename, 'utf-8'),
            bytes(output_filename, 'utf-8'),
            is_log)


def main():
    cur_path = os.getcwd()
    lib = AppspecDllWrapper()

    # calc
    input_filename = os.path.join(cur_path, 'appspec_input.json')
    res = lib.calc_apparatus_spectrum(input_filename)
    if res:
        print("Apparatus spectrum calculation error {}".format(res))
        sys.exit()

    convert_from_bin_to_txt('appspec_output.bin', 'appspec_output.txt')

    print('done')


if __name__ == '__main__':
    main()
