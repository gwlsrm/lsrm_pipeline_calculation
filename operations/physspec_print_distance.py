import json
import os
import typing as tp

from operations.operation_registry import register_operation
from .common_code.physspec_distance_calculation import (
    calc_distance_from_cap_to_crystal_center,
    calc_source_half_width,
)


def _get_distance_from_coordinates(input_filename: str) -> float:
    with open(input_filename) as f:
        data = json.load(f)

    det_center = calc_distance_from_cap_to_crystal_center(data["Detector"])
    source_width = calc_source_half_width(data["ContainerSource"])
    det_y_coord = data["ContainerSource"]["DetectorPosition"]["detY"]
    assert data["ContainerSource"]["DetectorPosition"]["detX"] == 0
    assert data["ContainerSource"]["DetectorPosition"]["detZ"] == 0
    distance = det_y_coord - source_width - det_center
    return distance


@register_operation
class PhysspecPrintDistance:
    """
    PhysspecPrintDistance converts detector coordinates to detector-object distance
        and prints it
    parameters:
        input_filename: physspec_input.json
    """
    def __init__(self):
        self.input_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'PhysspecPrintDistance'):
        op = PhysspecPrintDistance()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        return op

    def run(self) -> None:
        print('start physspec_print_distance')
        distance = _get_distance_from_coordinates(self.input_filename)
        print("det to source distance:", distance)
