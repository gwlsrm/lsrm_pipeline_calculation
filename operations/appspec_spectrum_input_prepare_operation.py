import csv
import json
import os
import typing as tp

from operations.operation_registry import register_operation


MIN_FLOAT = 1e-15
RESPONSE_JSON_TO_CSV_NAMES = {
    "Energy": "energy",
    "fep": "fep",
    "sep": "sep",
    "dep": "dep",
    "p511": "p511",
    "xep_total": "xept",
    "dfep": "dfep",
    "dsep": "dsep",
    "ddep": "ddep",
    "dp511": "dp511",
    "dxep_total": "dxept",
    "normalized_fep": "FEP",
    "normalized_sep": "SEP",
    "normalized_dep": "DEP",
    "normalized_p511": "P511",
    "normalized_xep_total": "XEPT",
    "e_xep": "exep",
    "xep": "xep",
    "dxep": "dxep",
    "normalized_xep": "XEP",
}


def _list_func(value: str) -> list[float]:
    return [float(token) for token in value.split(';')]


CSV_NAME_TO_FUNC = {
    "exep": _list_func,
    "xep": _list_func,
    "dxep": _list_func,
    "XEP": _list_func,
}


def _parse_response_row(row: tp.List[str], header: tp.Dict[str, int]) -> tp.Dict[str, tp.Any]:
    res = {}
    for j_name, c_name in RESPONSE_JSON_TO_CSV_NAMES.items():
        idx = header[c_name]
        f = CSV_NAME_TO_FUNC.get(c_name, float)
        value = f(row[idx])
        res[j_name] = value
    # a-array
    res["a"] = []
    for i in range(6):
        for j in range(9):
            c_name = f"a{i}{j}"
            idx = header[c_name]
            value = float(row[idx])
            res["a"].append(value)
    # b-array
    res["b"] = []
    for i in range(2):
        for j in range(9):
            c_name = f"b{i}{j}"
            idx = header[c_name]
            value = float(row[idx])
            res["b"].append(value)
    return res


def _parse_response_output(
        input_filename: str) -> tp.Dict[str, tp.Any]:
    responses = []
    with open(input_filename) as f:
        reader = csv.reader(f, delimiter=",")
        header = None
        for row in reader:
            if header is None:
                header = {name: i for i, name in enumerate(row)}
                continue
            responses.append(
                _parse_response_row(row, header)
            )
    return {
        "Emin": responses[0]["Energy"],
        "Emax": responses[-1]["Energy"],
        "N_points": len(responses),
        "Nmin": 100,
        "Nmax": 1000,
        "Response": responses,
    }


def _parse_physspec_output_full(input_filename: str) -> tp.Dict[str, tp.Any]:
    with open(input_filename) as f:
        data = json.load(f)["CalculationResults"]
    res = {}
    res["UncollidedFlux"] = data["func"]
    res["dUncollidedFlux"] = data["dfunc"]
    res["CollidedFlux"] = data["fcol"]
    res["dCollidedFlux"] = data["dfcol"]
    res["PeaksIntensity"] = data["y0"]
    res["PeaksEnergy"] = data["x1"]
    res["PeaksArea"] = data["y1"]
    res["PeaksdArea"] = data["dy1"]
    res["ContinuumEnergies"] = data["x2"]
    res["ContinuumCounts"] = data["y2"]
    # res["ContinuumdE"] = 0
    return res


def _read_json_data(input_filename: str) -> tp.Dict[str, tp.Any]:
    with open(input_filename) as f:
        return json.load(f)


def _write_appspec_input_file(
        output_filename: str,
        response: tp.Dict[str, tp.Any],
        physspec_data: tp.Dict[str, tp.Any],
        analyzer_data: tp.Dict[str, tp.Any],
        resp_mtx_data: tp.Dict[str, tp.Any],
        to_indent: bool = False):
    data = {
        "DetectorResponse": response,
        "PhysSpec": physspec_data,
    } | resp_mtx_data | analyzer_data
    indent = 4 if to_indent else None
    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=indent)


@register_operation
class AppspecSpectrumInputOperation:
    """
    AppspecSpectrumInputOperation creates input file for appspec spectrum calculation
    parameters:
        - input_response_filename: output csv-file from response calculation
        - input_physspec_filename: output json-file from physspec calculation
        - input_analyzer_filename: input filename with analyzer
        - input_response_matrix_filename: input filename with response matrix
        - output_filename: desirable input filename for appspec calculation
        - to_indent_output: add spaces and CR to json or create one-line json
    """
    def __init__(self):
        self.input_response_filename = ""
        self.input_physspec_filename = ""
        self.input_analyzer_filename = ""
        self.input_response_matrix_filename = ""
        self.output_filename = ""
        self.to_indent_output = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'AppspecSpectrumInputOperation'):
        op = AppspecSpectrumInputOperation()
        op.input_response_filename = os.path.join(project_dir, section['input_response_filename'])
        op.input_physspec_filename = os.path.join(project_dir, section['input_physspec_filename'])
        op.input_analyzer_filename = os.path.join(project_dir, section['input_analyzer_filename'])
        op.input_response_matrix_filename = os.path.join(project_dir, section['input_response_matrix_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.to_indent_output = section.get('to_indent_output', op.to_indent_output)
        return op

    def run(self) -> None:
        print('start apspec_efficiency_prepare')
        response = _parse_response_output(self.input_response_filename)
        physspec_data = _parse_physspec_output_full(self.input_physspec_filename)
        analyzer_data = _read_json_data(self.input_analyzer_filename)
        resp_mtx_data = _read_json_data(self.input_response_matrix_filename)
        # write'em all to output-file
        _write_appspec_input_file(self.output_filename, response, physspec_data, analyzer_data,
                                  resp_mtx_data, self.to_indent_output)
