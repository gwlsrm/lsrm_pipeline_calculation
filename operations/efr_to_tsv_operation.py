import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers import efaparser

EPS = 1e-15


def _parse_efr_output(input_filename: str) -> tp.List[efaparser.EffPoint]:
    eff = efaparser.get_efficiency_from_efa(input_filename)
    return eff.points


def _save_to_tsv(eff_points: tp.List[efaparser.EffPoint], output_filename: str):
    with open(output_filename, 'w') as f:
        # save header
        f.write(
            "\t".join(["energy", "efficiency", "defficiency", "count_rate", "dcount_rate",
                       "intensity"])
        )
        f.write("\n")
        # save data
        for eff_point in eff_points:
            f.write(
                "\t".join(
                    [str(v) for v in [eff_point.energy, eff_point.eff, eff_point.deff,
                                      eff_point.area, eff_point.darea, eff_point.intens]]
                )
            )
            f.write("\n")


@register_operation
class EfrToTsvOperation:
    """
    EfrToTsvOperation converts efr-file to tsv-file (like appspec output)
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'EfrToTsvOperation':
        op = EfrToTsvOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        return op

    def run(self) -> None:
        print('start efr_to_tsv')
        eff_points = _parse_efr_output(self.input_filename)

        _save_to_tsv(eff_points, self.output_filename)
