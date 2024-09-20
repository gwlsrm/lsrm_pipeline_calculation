import typing as tp
from dataclasses import dataclass

import numpy as np

from .efaparser import get_efficiency_from_efa, EffZone, Efficiency


# polynomial functions
def poly_reverse(poly_coeffs: tp.Iterable[float], x: float) -> float:
    assert len(poly_coeffs) > 0
    res = 0
    for c in poly_coeffs:
        res = res * x + c
    return res


def poly(poly_coeffs: tp.Iterable[float], x: float) -> float:
    assert len(poly_coeffs) > 0
    res = 0
    x_val = 1
    for c in poly_coeffs:
        res += c * x_val
        x_val *= x
    return res


# Usual polynomials
def get_original_poly_calib(x: np.ndarray, y: np.ndarray, degree: int = 1
                            ) -> tp.Tuple[np.ndarray, float]:
    X = np.array([
        [x_i**k for k in range(degree+1)]
        for x_i in x
    ])
    theta = np.linalg.inv(X.T @ X) @ X.T @ y
    theta_, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    theta = theta_
    L = (y - X @ theta)
    L = L.T @ L
    return theta, L


# orth polynomials calculation
def calc_orth_poly(g: np.ndarray, x: np.ndarray) -> float:
    return np.sum([poly(g, x_i) for x_i in x])


def calc_orth_poly_with_x_degree(g: np.ndarray, x: np.ndarray, degree: int) -> float:
    return np.sum([poly(g, x_i) * x_i**degree for x_i in x])


def add_orth_poly_coeffs(G: np.ndarray, deg: int, x: np.ndarray):
    assert deg > 0
    j = deg
    A = np.zeros((j, j))
    b = np.zeros((j,))

    for k in range(j):
        for i in range(j):
            A[k][i] = calc_orth_poly_with_x_degree(G[k], x, i)
    for k in range(j):
        b[k] = -calc_orth_poly_with_x_degree(G[k], x, j)

    # c_j = np.linalg.solve(A, b)
    c_j_approx, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    G[j, 0:j] = c_j_approx[:]
    G[j, j] = 1.0


def create_polynomes(x: np.ndarray, y: np.ndarray, degree: int = 1):
    assert degree >= 0
    # orth. poly
    G = np.zeros((degree+1, degree+1))
    G[0, 0] = 1.0
    for deg in range(1, degree+1):
        add_orth_poly_coeffs(G, deg, x)

    # main coeffs
    X = np.array([
        [poly(G[k], x[i]) for k in range(degree+1)]
        for i in range(len(x))])
    main_c_approx_1, residuals_1, rank_1, s_1 = np.linalg.lstsq(X, y, rcond=None)
    main_c = main_c_approx_1
    L = (y - X @ main_c)
    L = L.T @ L
    return G, main_c, L


# use orth poly
def use_orth_poly_calib(x_i: float, G: np.ndarray, main_c: np.ndarray) -> float:
    coeffs = G.T @ main_c
    return poly(coeffs, x_i)


# convert to usual poly coeffs
def convert_orth_to_usual(G: np.ndarray, main_c: np.ndarray) -> np.ndarray:
    return G.T @ main_c


def convert_orth_to_lsrm(orth_poly_coeffs: np.ndarray) -> tp.List[tp.List[float]]:
    res = []
    for i, g in enumerate(orth_poly_coeffs):
        g = g[:i+1]
        g = g[::-1]
        res.append(g.tolist())
    return res


@dataclass
class ZoneConfig:
    degree: int
    left_boundary: float
    right_boundary: float


def approx_efr_with_polynomes(eff: Efficiency, zones_config: tp.List[ZoneConfig]):
    eff.zones = []
    x = np.log10([p.energy for p in eff.points])
    y = np.log10([p.eff for p in eff.points])
    # create poly for every zone
    for zc in zones_config:
        x_l = np.log10(zc.left_boundary)
        x_r = np.log10(zc.right_boundary)
        x_z = x[(x_l <= x) & (x <= x_r)]
        y_z = y[(x_l <= x) & (x <= x_r)]
        assert len(x_z) > zc.degree
        orth_coeffs, main_c, loss = create_polynomes(x_z, y_z, degree=zc.degree)
        zone = EffZone(zc.degree, x_l, x_r, np.sqrt(loss / (len(x_z) - zc.degree)),
                       main_c.tolist(), convert_orth_to_lsrm(orth_coeffs))
        eff.zones.append(zone)
    return eff


def approx_with_polynomes(efr_filename: str, zones_config: tp.List[ZoneConfig]):
    eff = get_efficiency_from_efa(efr_filename)
    return approx_efr_with_polynomes(eff, zones_config)


DEFAULT_ZONES_CONFIG = [ZoneConfig(4, 50, 400.0), ZoneConfig(2, 250, 3000.0)]


def main():
    eff = approx_with_polynomes("test.efa", [
        ZoneConfig(5, 50, 400.0), ZoneConfig(2, 250, 3000.0)])
    eff.save_as_efa("test_1.efa")


if __name__ == "__main__":
    main()
