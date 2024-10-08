import os
import typing as tp

from operations.operation_registry import register_operation

from .lsrm_parsers import efaparser
from .lsrm_code_internal import orth_poly_lsrm


@register_operation
class AutoEfficiencyCalibrationOperation:
    """
    AutoEfficiencyCalibrationOperation make auto efficiency for efr-file and
        saves approximation to efa-file
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.zones_config = orth_poly_lsrm.DEFAULT_ZONES_CONFIG
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
                    orth_poly_lsrm.ZoneConfig(z["degree"], z["left"], z["right"])
                )
        assert len(op.zones_config) > 0
        op.is_append = section.get("is_append", op.is_append)
        return op

    def run(self) -> None:
        print('start auto_efficiency_calibration')
        efr = efaparser.get_efficiency_from_efa(self.input_filename)
        efa = orth_poly_lsrm.approx_efr_with_polynomes(efr, self.zones_config)
        efa.convert_recordname_to_efa()
        efa.save_as_efa(self.output_filename, self.is_append)
