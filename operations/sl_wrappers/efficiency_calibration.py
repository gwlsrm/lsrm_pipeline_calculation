import typing as tp
from dataclasses import dataclass

import numpy as np

from operations.lsrm_parsers.efaparser import get_efficiency_from_efa, Efficiency, EffZone
from .orth_poly_wrapper import OrthogonalPolynomialWrapper


@dataclass
class ZoneConfig:
    degree: int
    left_boundary: float
    right_boundary: float


DEFAULT_ZONES_CONFIG = [ZoneConfig(4, 50, 400.0), ZoneConfig(2, 250, 3000.0)]


def convert_orth_to_lsrm(orth_poly_coeffs: tp.List[tp.List[float]]) -> tp.List[tp.List[float]]:
    res = []
    for i, g in enumerate(orth_poly_coeffs):
        g = g[:i+1]
        res.append(g)
    return res


def approx_efr_with_polynomes(eff: Efficiency, zones_config: tp.List[ZoneConfig]):
    eff.zones = []
    x = np.log10([p.energy for p in eff.points])
    y = np.log10([p.eff for p in eff.points])
    dyplus = np.log10([1.0 + p.deff/100.0 for p in eff.points])
    dyminus = -np.log10([1.0 - p.deff/100.0 for p in eff.points])
    dy = np.maximum(dyplus, dyminus)
    dy = dyplus
    w = 1/dy**2
    lib = OrthogonalPolynomialWrapper()
    # create poly for every zone
    for zc in zones_config:
        x_l = np.log10(zc.left_boundary)
        x_r = np.log10(zc.right_boundary)
        x_z = x[(x_l <= x) & (x <= x_r)]
        y_z = y[(x_l <= x) & (x <= x_r)]
        w_z = w[(x_l <= x) & (x <= x_r)]
        assert len(x_z) > zc.degree
        eff_poly = lib.approximate_orthogonal_polynomials(x_z, y_z, w_z, degree=zc.degree)
        zone = EffZone(zc.degree, x_l, x_r, eff_poly.quality,
                       eff_poly.main_coeffs, convert_orth_to_lsrm(eff_poly.orth_poly_coeffs))
        eff.zones.append(zone)
    return eff


def approx_with_polynomes(efr_filename: str, zones_config: tp.List[ZoneConfig]):
    eff = get_efficiency_from_efa(efr_filename)
    return approx_efr_with_polynomes(eff, zones_config)


def main():
    eff = approx_with_polynomes("Gem15P4_EffCalc.efa", [
        ZoneConfig(4, 33.07, 339.74), ZoneConfig(3, 187.13, 3393.0)])
    eff.save_as_efa("test_2.efa")


if __name__ == "__main__":
    main()
