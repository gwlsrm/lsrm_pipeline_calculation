import csv
import json
import os
import typing as tp

from operations.operation_registry import register_operation


MIN_FLOAT = 1e-15


def _parse_response_output(
        input_filename: str) -> tp.Tuple[tp.List[float], tp.List[float], tp.List[float]]:
    with open(input_filename) as f:
        reader = csv.reader(f, delimiter=",")
        header = None
        resp_energies = []
        resp_nfep = []
        resp_dfep = []
        for row in reader:
            if header is None:
                header = {name: i for i, name in enumerate(row)}
                continue
            resp_energies.append(float(row[header["energy"]]))
            resp_nfep.append(float(row[header["FEP"]]))
            resp_dfep.append(float(row[header["dfep"]]))
    return resp_energies, resp_nfep, resp_dfep


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


def _write_appspec_input_file(
        output_filename: str,
        resp_energies: tp.List[float], resp_nfep: tp.List[float], resp_dfep: tp.List[float],
        physspec_data: tp.Dict[str, tp.Any],
        to_indent: bool = False):
    data = {}
    data["DetectorResponse"] = []
    for e, fep, dfep in zip(resp_energies, resp_nfep, resp_dfep):
        data["DetectorResponse"].append({
            "Energy": e,
            "normalized_fep": fep,
            "dfep": dfep
        })
    data["PhysSpec"] = physspec_data
    indent = 4 if to_indent else None
    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=indent)


@register_operation
class AppspecEfficiencyInputOperation:
    """
    AppspecEfficiencyInputOperation creates input file for appspec efficiency calculation
    parameters:
        - input_response_filename: output csv-file from response calculation
        - input_physspec_filename: output json-file from physspec calculation
        - output_filename: desirable input filename for appspec calculation
        - to_indent_output: add spaces and CR to json or create one-line json
    """
    def __init__(self):
        self.input_response_filename = ""
        self.input_physspec_filename = ""
        self.output_filename = ""
        self.to_indent_output = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'AppspecEfficiencyInputOperation'):
        op = AppspecEfficiencyInputOperation()
        op.input_response_filename = os.path.join(project_dir, section['input_response_filename'])
        op.input_physspec_filename = os.path.join(project_dir, section['input_physspec_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.to_indent_output = section.get('to_indent_output', op.to_indent_output)
        return op

    def run(self) -> None:
        print('start apspec_efficiency_prepare')
        # get energies, nfep, dfep from response
        resp_energies, resp_nfep, resp_dfep = _parse_response_output(self.input_response_filename)
        # get energies, crs, intensities from physspec_output
        physspec_data = _parse_physspec_output_full(self.input_physspec_filename)
        # write'em all to output-file
        _write_appspec_input_file(self.output_filename, resp_energies, resp_nfep, resp_dfep,
                                  physspec_data, self.to_indent_output)
