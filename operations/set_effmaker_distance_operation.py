import json
import os
import typing as tp

from operations.operation_registry import register_operation


def _calc_distance_from_cap_to_crystal_center(
        det_data: tp.Dict[str, tp.Any]) -> float:
    geom = det_data["Geometry"]
    if det_data["Type"].upper() == "COAXIAL":
        return (
            geom["CrystalHeight"] / 2 +
            geom["CapToCrystalDistance"] +
            geom["DetectorCapFrontThickness"])
    elif det_data["Type"].upper() == "SCINTILLATOR":
        return (
            geom["CrystalHeight"] / 2 +
            geom["CrystalFrontReflectorThickness"] +
            geom["CrystalFrontCladdingThickness"] +
            geom["DetectorFrontPackagingThickness"] +
            geom["DetectorFrontCapThickness"]
        )
    elif det_data["Type"].upper() == "COAX_WELL":
        raise RuntimeError("COAX_WELL cannot be used with EffMaker")
    else:
        raise RuntimeError(f"unrealized operation for detector type: {det_data['Type']}")


def _calc_source_half_width(source_data: tp.Dict[str, tp.Any]) -> float:
    outer_cell = source_data["Cells"][0]
    if outer_cell["Shape"] == "Point":
        return 0
    dimensions = outer_cell["Dimensions"]
    if outer_cell["Shape"] == "CylZ":
        return dimensions["Dim2"]
    elif outer_cell["Shape"] == "Cuboid":
        return dimensions["Dim3"] / 2
    elif outer_cell["Shape"] == "Sphere":
        return dimensions["Dim1"]
    elif outer_cell["Shape"] == "ConeZ":
        return (dimensions["Dim2"] + dimensions["Dim3"]) / 2
    elif outer_cell["Shape"] == "ChamferedCuboidZ":
        return dimensions["Dim3"] / 2
    else:
        raise RuntimeError(f'unrealized operation for source type: {outer_cell["shape"]}')


def _sets_det_y_coordinate(input_filename: str, distance: float, output_filename: str,
                           indent: bool = False) -> None:
    with open(input_filename) as f:
        data = json.load(f)

    # det height
    det_center = _calc_distance_from_cap_to_crystal_center(data["Detector"])

    # source width
    source_width = _calc_source_half_width(data["ContainerSource"])

    det_y_coord = source_width + distance + det_center

    # set to output file
    data["ContainerSource"]["DetectorPosition"]["detY"] = det_y_coord

    indent = 4 if indent else None
    with open(output_filename, 'w') as g:
        json.dump(data, g, indent=indent)


@register_operation
class SetEffMakerDistanceOperation:
    """
    SetEffMakerDistanceOperation converts detector-object distance to detector coordinates
        and sets it to physspec_input.json
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.distance = 0.0
        self.to_indent_output = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'SetEffMakerDistanceOperation'):
        op = SetEffMakerDistanceOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.distance = section["distance"]
        op.to_indent_output = section.get('to_indent_output', op.to_indent_output)
        return op

    def run(self) -> None:
        print('start set effmaker distance')
        _sets_det_y_coordinate(self.input_filename, self.distance, self.output_filename,
                               self.to_indent_output)
