import os
import typing as tp

import matplotlib.pyplot as plt
import numpy as np

from operations.operation_registry import register_operation
from .lsrm_parsers import efaparser


@register_operation
class PlotEfficiencyOperation:
    """
    PlotEfficiencyOperation plots efficiency from efa or efr file and saves it to the image file
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.efficiency_name = ""
        self.draw_points = True

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'PlotEfficiencyOperation':
        op = PlotEfficiencyOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.efficiency_name = section.get("efficiency_name", op.efficiency_name)
        op.draw_points = section.get("draw_points", op.draw_points)
        return op

    def run(self) -> None:
        print('start plot efficiency operation')
        if self.efficiency_name:
            eff = efaparser.get_eff_by_name(self.input_filename, self.efficiency_name)
        else:
            eff = efaparser.get_efficiency_from_efa(self.input_filename)
        has_approx = len(eff.zones) > 0
        assert has_approx or self.draw_points, "need something to draw"

        # energy range
        en_from, en_to = eff.get_energy_range_kev()
        # data for graphs
        point_energies = np.array([p.energy for p in eff.points])
        point_effs = np.array([p.eff for p in eff.points])
        if has_approx:
            energies = np.geomspace(en_from, en_to, 20)
            eff_deffs = [eff.get_eff(e) for e in energies]
            effs = np.array([r[0] for r in eff_deffs])
            deffs_plus = np.array([r[0]* (1 + r[1]) for r in eff_deffs])
            deffs_minus = np.array([r[0]* (1 - r[1]) for r in eff_deffs])
        # plot
        plt.figure()
        if self.draw_points:
            plt.scatter(point_energies, point_effs)
        if has_approx:
            plt.plot(energies, effs)
            plt.plot(energies, deffs_plus)
            plt.plot(energies, deffs_minus)
        plt.xscale('log')
        plt.yscale('log')
        plt.savefig(self.output_filename)
