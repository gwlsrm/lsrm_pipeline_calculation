import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation

from .lsrm_parsers import efaparser

EPS = 1e-15


def _create_energy_grid(energy_grid: tp.Dict[str, tp.Any]) -> tp.List[float]:
    if energy_grid["is_log"]:
        return np.geomspace(energy_grid["start"], energy_grid["end"], energy_grid["points"])
    else:
        return np.linspace(energy_grid["start"], energy_grid["end"], energy_grid["points"])


def _get_efa(input_filename: str, section_name: str) -> efaparser.Efficiency:
    if section_name:
        eff = efaparser.get_eff_by_name(input_filename, section_name)
    else:
        eff = efaparser.get_efficiency_from_efa(input_filename)
    if eff is None:
        raise RuntimeError("No efficiency in efa")
    return eff


def _convert_to_efr(efficiency: efaparser.Efficiency,
                    energy_points: tp.List[float]) -> efaparser.Efficiency:
    eff_points = []
    for e in energy_points:
        eff, deff = efficiency.get_eff(e)
        eff_points.append(efaparser.EffPoint(e, eff, deff, "nuclide", 100, 1, 1))
    efficiency.points = eff_points
    efficiency.convert_records_to_efr("nuclide")
    return efficiency


@register_operation
class EfrFromEfaOperation:
    """
    EfrFromEfaOperation creates efr from efa and energy point grid.
    Energy grid can be set by energy points or by parameters (not both).
    If no energy grid is set, it will be taken from efa.
    parameters:
        input_filename: efa-filename
        section_name: section name in efa-file (full string with "[", "]"),
            if empty first section will be taken
        output_filename: desired result efr-filename
        energy_points: energy grid (array of energies in keV) for efr, optional
        energy_grid: energy grid by parameters: dictionary with start, end, points, is_log,
            optional
    """
    def __init__(self):
        self.input_filename = ""
        self.section_name = ""
        self.output_filename = ""
        self.energy_points = None

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EfrFromEfaOperation':
        op = EfrFromEfaOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.energy_points = section.get("energy_points")
        if not op.energy_points:
            energy_grid = section.get("energy_grid")
            if energy_grid:
                op.energy_points = _create_energy_grid(energy_grid)
        return op

    def run(self) -> None:
        print('start efr_from_efa operation')
        efficiency = _get_efa(self.input_filename, self.section_name)
        if self.energy_points is None:
            self.energy_points = [p.energy for p in efficiency.points]
        assert len(self.energy_points) > 0

        efr = _convert_to_efr(efficiency, self.energy_points)
        efr.save_as_efr(self.output_filename)
