import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation
from .common_parsers.tsv_parser import parse_tsv_to_cols
from .lsrm_parsers.mu import MuDB, get_material_mus, Material

keV2MeV = 1000
g2kg = 0.001


def _load_point_efficiency(input_filename: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """returns arrays: energy, efficiency and defficiency"""
    res = parse_tsv_to_cols(input_filename)
    return np.array(res['energy']), np.array(res['efficiency']), np.array(res['defficiency'])


def _load_mu(material: Material, energies: np.ndarray) -> np.ndarray:
    mu_db = MuDB.read_from_directory("XCOM")
    return np.array(get_material_mus(material, mu_db, energies / keV2MeV))


def calculate_extended_object_efficiency(
        energies: np.ndarray, point_efficiency: np.ndarray, distance: float, material: Material
    ) -> np.ndarray:
    mu = _load_mu(material, energies)
    return point_efficiency * distance**2 * 2 * np.pi / mu * g2kg


def _save_to_tsv(energies: np.ndarray, efficiency: np.ndarray, defficiency: np.ndarray, output_filename: str):
    with open(output_filename, 'w') as f:
        # save header
        f.write(
            "\t".join(["energy", "efficiency", "defficiency"])
        )
        f.write("\n")
        # save data
        for e, eff, deff in zip(energies, efficiency, defficiency):
            f.write("\t".join([str(v) for v in [e, eff, deff]]))
            f.write("\n")


@register_operation
class ExtendedObjectEfficiencyOperation:
    """
    ExtendedObjectEfficiencyOperation calculates efficiency for extended objects
    eff = eff_point * r^2 * 2pi / mu(E)
    params:
        input_filename: str -- point efficiency tsv-file
        distance: float -- distance of point efficiency, cm
        material_formula: str -- material formula like H2O1
        material_json: str -- material in json-format: {name: ..., rho: ..., elements: [{z:..., frac: ...}, ...]}
            e.g. {"name": "water", "rho": 1.0, "elements": [{"z": 1, "frac": 0.11}, {"z": 8, "frac": 0.89}]}
        sl_material_json: str -- material in json-format: {Name: ..., Ro: ..., Compound: [{"z": frac}, ...]}
            e.g. {"Name": "water", "Ro": 1.0, "Compound": [{"1": 0.11}, {"8": 0.89}]}
        output_filename: str -- specific efficiency tsv-file in kg/(Bq * s)
    """
    def __init__(self):
        self.input_filename = ""
        self.distance = 0.0
        self.material_formula = ""
        self.material_json = ""
        self.sl_material_json = ""
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'ExtendedObjectEfficiencyOperation':
        op = ExtendedObjectEfficiencyOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.distance = float(section['distance'])
        op.material_formula = section.get('material_formula', "")
        op.material_json = section.get('material_json', "")
        op.sl_material_json = section.get('sl_material_json', "")
        assert op.material_json or op.material_formula or op.sl_material_json, \
            "need to pass material_formula, material_json or sl_material_json"
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        return op

    def run(self) -> None:
        print('start extended object efficiency operation')
        energies, point_efficiency, defficiency = _load_point_efficiency(self.input_filename)
        if self.material_formula:
            material = Material.parse_from_formula(self.material_formula)
        elif self.material_json:
            material = Material.read_from_json(self.material_json)
        else:
            material = Material.read_from_sl_json(self.sl_material_json)
        ext_efficiency = calculate_extended_object_efficiency(energies, point_efficiency, self.distance, material)
        _save_to_tsv(energies, ext_efficiency, defficiency, self.output_filename)
