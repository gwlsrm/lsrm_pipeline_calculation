from .appspec_wrapper import AppspecDllWrapper
from .read_output_bin import convert_from_bin_to_txt


def calc_efficiency(input_filename: str, output_filename: str, is_log: bool) -> None:
    lib = AppspecDllWrapper()
    res = lib.calculate_efficiency_json(input_filename, output_filename, is_log)
    del lib
    if res != 0:
        raise RuntimeError(f"efficiency calculation error: {res}")


def calc_spectrum(input_filename: str, output_filename: str):
    lib = AppspecDllWrapper()

    res = lib.calc_apparatus_spectrum(input_filename)
    if res:
        raise RuntimeError("Apparatus spectrum calculation error {}".format(res))

    convert_from_bin_to_txt('appspec_output.bin', output_filename)
