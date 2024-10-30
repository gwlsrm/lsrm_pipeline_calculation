import ctypes as ct
import os.path
import typing as tp
from dataclasses import dataclass, field
from itertools import chain

import numpy as np


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


class _OrthogonalPolynomialsApproximation(ct.Structure):
    _fields_ = [
        ("main_coeffs", ct.POINTER(ct.c_double)),
        ("main_coeffs_size", ct.c_uint64),
        ("orth_poly_coeffs", ct.POINTER(ct.c_double)),
        ("orth_poly_coeffs_size", ct.c_uint64),
        ("quality", ct.c_double),
        ("chi2", ct.c_double),
    ]


@dataclass
class OrthogonalPolynomialsApproximation:
    main_coeffs: tp.List[float] = field(default_factory=list)
    orth_poly_coeffs: tp.List[tp.List[float]] = field(default_factory=list)
    quality: float = 0.0
    chi2: float = 0.0

    @staticmethod
    def create_from_ct(ct_opa: _OrthogonalPolynomialsApproximation
                       ) -> "OrthogonalPolynomialsApproximation":
        res = OrthogonalPolynomialsApproximation()
        for i in range(ct_opa.main_coeffs_size):
            res.main_coeffs.append(float(ct_opa.main_coeffs[i]))

        n = ct_opa.orth_poly_coeffs_size
        for i in range(n):
            res.orth_poly_coeffs.append([])
            for j in range(n):
                res.orth_poly_coeffs[-1].append(float(ct_opa.orth_poly_coeffs[i*n+j]))
        res.quality = float(ct_opa.quality)
        res.chi2 = float(ct_opa.chi2)
        return res


def make_c_struct(polynomials: OrthogonalPolynomialsApproximation) -> _OrthogonalPolynomialsApproximation:
    c_poly = _OrthogonalPolynomialsApproximation()
    c_poly.main_coeffs_size = ct.c_uint64(len(polynomials.main_coeffs))
    c_poly.main_coeffs = (ct.c_double * len(polynomials.main_coeffs))(*polynomials.main_coeffs)
    orth_poly_coeffs = list(chain.from_iterable(polynomials.orth_poly_coeffs))
    assert len(orth_poly_coeffs) == len(polynomials.orth_poly_coeffs)**2
    c_poly.orth_poly_coeffs_size = ct.c_uint64(len(polynomials.orth_poly_coeffs))
    c_poly.orth_poly_coeffs = (ct.c_double * len(orth_poly_coeffs))(*orth_poly_coeffs)
    c_poly.quality = ct.c_double(polynomials.quality)
    c_poly.chi2 = ct.c_double(polynomials.chi2)
    return c_poly


class OrthogonalPolynomialWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None):
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = ct.CDLL(os.path.join(path_to_dll, lib_name), ct.RTLD_GLOBAL)
        # funcs
        ## ApproximateOrthogonalPolynomials
        self._approximate_orthogonal_polynomials = _get_attribute(
            self._lib,
            ['ApproximateOrthogonalPolynomials']
        )
        self._approximate_orthogonal_polynomials.argtypes = [
            ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.c_uint,
            ct.c_int,
            ct.POINTER(_OrthogonalPolynomialsApproximation)]
        self._approximate_orthogonal_polynomials.restype = ct.c_int

        ## GetValueFromOrthogonalPolynomials
        self._get_value_from_orthogonal_polynomials = _get_attribute(
            self._lib,
            ['GetValueFromOrthogonalPolynomials']
        )
        self._get_value_from_orthogonal_polynomials.argtypes = [
            ct.POINTER(_OrthogonalPolynomialsApproximation),
            ct.c_double,
            ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)
        ]
        self._get_value_from_orthogonal_polynomials.restype = ct.c_int

        ## FreeOrthogonalPolinomialsMemory
        self._free_orthogonal_polynomials = _get_attribute(
            self._lib,
            ["FreeOrthogonalPolinomialsMemory"]
        )
        self._free_orthogonal_polynomials.argtypes = [
            ct.POINTER(_OrthogonalPolynomialsApproximation)]

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['orthogonal_polynomials.dll', 'liborthogonal_polynomials.dll',
                         'liborthogonal_polynomials.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find orthogonal_polynomials library in "{path_to_dll}"')

    def approximate_orthogonal_polynomials(
            self,
            x: tp.List[float], y: tp.List[float], w: tp.List[float],
            degree: int) -> OrthogonalPolynomialsApproximation:
        assert len(x) == len(y) == len(w), "arrays must have same lengths"
        size = len(x)
        xx = (ct.c_double * size)(*x)
        yy = (ct.c_double * size)(*y)
        ww = (ct.c_double * size)(*w)
        c_poly = _OrthogonalPolynomialsApproximation()
        err = self._approximate_orthogonal_polynomials(
            xx, yy, ww, size, degree, ct.pointer(c_poly)
        )
        if err != 0:
            raise RuntimeError(f"error code: {err}")
        res = OrthogonalPolynomialsApproximation.create_from_ct(c_poly)
        self._free_orthogonal_polynomials(c_poly)
        return res

    def get_value_from_orthogonal_polynomials(self,
            polynomials: OrthogonalPolynomialsApproximation, x: float) -> tp.Tuple[float, float]:
        c_poly = make_c_struct(polynomials)
        y = ct.c_double(0.0)
        dy = ct.c_double(0.0)
        err = self._get_value_from_orthogonal_polynomials(
            c_poly, ct.c_double(x), ct.byref(y), ct.byref(dy)
        )
        if err != 0:
            raise RuntimeError(f"error code: {err}")
        return float(y.value), float(dy.value)


def _load_example_input():
    data = [0]*8
    data[0] = (50.0,    3.42396e-07, 0.263343321767778)
    data[1] = (62.0236, 4.04239e-06, 0.219937957495442)
    data[2] = (76.9385, 1.7531e-05,  0.176076664194855)
    data[3] = (95.4401, 3.84041e-05, 0.167350621418026)
    data[4] = (118.391, 5.57345e-05, 0.162144093873633)
    data[5] = (146.86,  6.6887e-05,  0.166797733490813)
    data[6] = (182.176, 6.99682e-05, 0.176428720475873)
    data[7] = (225.984, 6.87986e-05, 0.191245170686613)
    xs = []
    ys = []
    ws = []
    for x, y, w in data:
        xs.append(np.log10(x))
        ys.append(np.log10(y))
        ws.append(np.log10(1.0 + w / 100.0))
        ws[-1] = 1.0 / (ws[-1]**2)
    return xs, ys, ws


def main():
    lib = OrthogonalPolynomialWrapper()

    # approximate
    # lib.test_func(x)
    x, y, w = _load_example_input()
    polys = lib.approximate_orthogonal_polynomials(x, y, w, 4)
    print("Main coeffs:")
    print(polys.main_coeffs)
    print("orth_poly:")
    print(polys.orth_poly_coeffs)
    print("quality:", polys.quality)
    print("chi2:", polys.chi2)

    # get value from approximation
    x_t = 60.0
    x_test = np.log10(x_t)
    y_test, dy_test = lib.get_value_from_orthogonal_polynomials(polys, x_test)
    print("get value result:")
    print(f"{x_test} -> {y_test}, {dy_test}")
    print(f"{x_t} -> {10**y_test}, {10**dy_test}")


if __name__ == "__main__":
    main()
