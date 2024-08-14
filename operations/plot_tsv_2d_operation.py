import os
import typing as tp

import matplotlib.pyplot as plt

from operations.operation_registry import register_operation


def _load_cols_from_tsv(filename: str, x_col_name: str, y_col_name: str) -> (
        tp.Tuple[tp.List[float], tp.List[float]]):
    header_names = None
    x = []
    y = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if header_names is None:
                header_names = {w: i for i, w in enumerate(line.split('\t'))}
                assert x_col_name in header_names and y_col_name in header_names
                continue
            tokens = [float(w) for w in line.split('\t')]
            assert len(tokens) == len(header_names)
            x.append(tokens[header_names[x_col_name]])
            y.append(tokens[header_names[y_col_name]])
    return x, y


@register_operation
class PlotTsv2dOperation:
    """
    PlotTsv2dOperation plots 2d-graph from 2 cols from tsv-file and saves it to image-file
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.x_col_name = None
        self.y_col_name = None
        self.x_scale_log = False
        self.y_scale_log = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'PlotTsv2dOperation':
        op = PlotTsv2dOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.x_col_name = section["x_col_name"]
        op.y_col_name = section["y_col_name"]
        op.x_scale_log = section.get("x_scale_log", op.x_scale_log)
        op.y_scale_log = section.get("y_scale_log", op.y_scale_log)
        return op

    def run(self) -> None:
        print('start plot 2d operation')
        x, y = _load_cols_from_tsv(self.input_filename, self.x_col_name, self.y_col_name)
        plt.figure()
        if self.x_scale_log:
            plt.xscale('log')
        if self.y_scale_log:
            plt.yscale('log')
        plt.scatter(x, y)
        plt.plot(x, y)
        plt.savefig(self.output_filename)
