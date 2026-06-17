import os
import typing as tp

from operations.operation_registry import register_operation

from .common_parsers.tsv_parser import parse_tsv_to_cols
from .lsrm_parsers import efaparser

EPS = 1e-15


def _parse_efr(input_filename: str) -> efaparser.Efficiency:
    eff = efaparser.get_efficiency_from_efa(input_filename)
    assert eff is not None
    return eff

def _load_tsv_values(input_filename: str, columns: tp.List[str]) -> dict[str, list[tp.Any]]:
    """returns arrays: energy, efficiency and defficiency"""
    res = parse_tsv_to_cols(input_filename)
    return {col: res[col] for col in columns}


def _update_efr(eff: efaparser.Efficiency, tsv_values: dict[str, list[tp.Any]]) -> efaparser.Efficiency:
    """updates efr-file from tsv-file"""
    assert len(eff.points) == len(tsv_values['energy']), f"now supported only equal recs: {len(eff.points)} != {len(tsv_values['energy'])}"
    for i, point in enumerate(eff.points):
        if 'energy' in tsv_values:
            point.energy = float(tsv_values['energy'][i])
        if 'efficiency' in tsv_values:
            point.eff = float(tsv_values['efficiency'][i])
        if 'defficiency' in tsv_values:
            point.deff = float(tsv_values['defficiency'][i])
    return eff


@register_operation
class EfrUpdateFromTsvOperation:
    """
    EfrUpdateFromTsvOperation updates efr-file from tsv-file
    """
    def __init__(self):
        self.efr_filename = ""
        self.tsv_filename = ""
        self.columns = []
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EfrUpdateFromTsvOperation':
        op = EfrUpdateFromTsvOperation()
        op.efr_filename = os.path.join(project_dir, section['efr_filename'])
        op.tsv_filename = os.path.join(project_dir, section['tsv_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.columns = section['columns']
        for col in op.columns:
            assert col in ['energy', 'efficiency', 'defficiency'], f"Unknown column {col}"
        return op

    def run(self) -> None:
        print('start efr_update_from_tsv')
        eff = _parse_efr(self.efr_filename)
        tsv_values = _load_tsv_values(self.tsv_filename, self.columns)
        new_eff = _update_efr(eff, tsv_values)
        new_eff.save_as_efr(self.output_filename)
