import bisect
import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation


# mods
LINEAR = "linear"
REVERSE_LINEAR = "reverse_linear"
LINEAR_LOG = "linear_log"
AVAILIABLE_MODS = [LINEAR, REVERSE_LINEAR, LINEAR_LOG]


def _get_close_indices(distances: tp.List[float], target_distance: float) -> tp.Tuple[float, float]:
    ri = bisect.bisect_left(distances, target_distance)
    if ri == len(distances):
        ri -= 1
    elif ri == 0:
        ri += 1
    li = ri - 1
    assert 0 <= li and ri < len(distances)
    return li, ri


def _parse_tsv_output(filename: str) -> tp.Dict[str, np.ndarray]:
    header_names = None
    res: tp.Dict[str, tp.List[float]] = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if header_names is None:
                header_names = [w for w in line.split('\t')]
                continue
            tokens = [float(w) for w in line.split('\t')]
            assert len(tokens) == len(header_names)
            for name, value in zip(header_names, tokens):
                res.setdefault(name, [])
                res[name].append(value)
    return {k: np.array(v) for k, v in res.items()}


def _load_efficiency(filename: str) -> tp.Dict[str, np.ndarray]:
    if not filename.endswith(".tsv"):
        raise RuntimeError("Unsupported file extension, please, use .tsv-files")
    return _parse_tsv_output(filename)


def _save_tsv(res: tp.Dict[str, tp.List[float]], output_filename: str):
    with open(output_filename, 'w') as f:
        f.write('\t'.join(res.keys()))
        f.write('\n')
        for k in res.keys():
            n = len(res[k])
            break
        for i in range(n):
            f.write("\t".join([str(v[i]) for v in res.values()]))
            f.write('\n')


def _save_efficiency(res: tp.Dict[str, tp.List[float]], output_filename: str):
    if not output_filename.endswith(".tsv"):
        raise RuntimeError("Unsupported file extension, please, use .tsv-files")
    _save_tsv(res, output_filename)


class LinearInterpol:
    def __init__(self, dist_left: float, dist_right: float, target_distance: float):
        self.w = (target_distance - dist_left) / (dist_right - dist_left)

    def __call__(self, left_a: np.ndarray, right_a: np.ndarray) -> np.ndarray:
        return (1 - self.w) * left_a + self.w * right_a


def _interpolate_efficiency_to_new_distance(input_filenames: tp.List[str], output_filename: str,
                                            distances: tp.List[float], target_distance: float,
                                            mode: str):
    li, ri = _get_close_indices(distances, target_distance)
    if mode == LINEAR:
        interpol = LinearInterpol(distances[li], distances[ri], target_distance)
    elif mode == REVERSE_LINEAR:
        interpol = LinearInterpol(1/distances[li], 1/distances[ri], 1/target_distance)
    elif mode == LINEAR_LOG:
        interpol = LinearInterpol(distances[li], distances[ri], target_distance)
    left_efficiency = _load_efficiency(input_filenames[li])
    right_efficiency = _load_efficiency(input_filenames[ri])

    res = {}
    for column_name, lvalues in left_efficiency.items():
        rvalues = right_efficiency[column_name]
        if mode == LINEAR_LOG and column_name == "efficiency":
            lvalues = np.log10(lvalues)
            rvalues = np.log10(rvalues)

        r = interpol(lvalues, rvalues)
        if mode == LINEAR_LOG and column_name == "efficiency":
            r = 10**r
        res[column_name] = r

    _save_efficiency(res, output_filename)


@register_operation
class LinearEfficiencyInterpolateOperation:
    """
    LinearEfficiencyInterpolateOperation linear interpolates efficiencies by distance
    """
    def __init__(self):
        self.input_filenames: tp.List[str] = []
        self.distances: tp.List[float] = []
        self.output_filename = ""
        self.target_distance = 0.0
        self.mode: str = LINEAR

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'LinearEfficiencyInterpolateOperation'):
        op = LinearEfficiencyInterpolateOperation()
        op.input_filenames = [
            os.path.join(project_dir, input_filename)
            for input_filename in section['input_filenames']]
        op.distances = section['distances']
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.target_distance = section['target_distance']
        assert len(op.input_filenames) == len(op.distances)
        assert len(op.distances) > 1, "nothing to interpolate"
        op.mode = section.get("mode", op.mode)
        assert op.mode in AVAILIABLE_MODS
        return op

    def run(self) -> None:
        print('start linear_efficiency_interpolate')
        _interpolate_efficiency_to_new_distance(self.input_filenames, self.output_filename,
                                                self.distances, self.target_distance, self.mode)
