import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers import efaparser
from .sl_wrappers import efficiency_calibration as ec


@register_operation
class AutoEfficiencyCalibrationOperation:
    """
    AutoEfficiencyCalibrationOperation make auto efficiency calibration for efr-file and
        saves approximation to efa-file.
    It needs liborthogonal_polynomials.so for work
    parameters:
        - input_filename: input efr file
        - output_filename: desirable name of the output efa filename
        - zones_config: list with zone to create: [{degree: 3, left: 50, right: 300}, ...]
        - is_append: append new efficiency section to file or create new one
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.zones_config = ec.DEFAULT_ZONES_CONFIG
        self.is_append = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str
                        ) -> 'AutoEfficiencyCalibrationOperation':
        op = AutoEfficiencyCalibrationOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        assert op.input_filename != op.output_filename
        if section.get("zone_config"):
            op.zones_config = []
            zones = section["zone_config"]
            for z in zones:
                op.zones_config.append(
                    ec.ZoneConfig(z["degree"], z["left"], z["right"])
                )
        assert len(op.zones_config) > 0
        op.is_append = section.get("is_append", op.is_append)
        return op

    def run(self) -> None:
        print('start auto_efficiency_calibration')
        efr = efaparser.get_efficiency_from_efa(self.input_filename)
        efa = ec.approx_efr_with_polynomes(efr, self.zones_config)
        efa.save_as_efa(self.output_filename, self.is_append)
