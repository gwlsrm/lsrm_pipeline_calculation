from .appspec_wrapper import AppspecDllWrapper


def calc_efficiency(input_filename: str, output_filename: str, is_log: bool) -> None:
    lib = AppspecDllWrapper()
    res = lib.calculate_efficiency_json(input_filename, output_filename, is_log)
    del lib
    if res != 0:
        raise RuntimeError(f"efficiency calculation error: {res}")
