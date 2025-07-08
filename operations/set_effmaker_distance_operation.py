import json
import math
import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation


EPSILON = 1e-6


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


def _get_angles(x: float, y: float, z: float) -> tp.Tuple[float, float, float]:
    R = math.sqrt(x**2 + y**2 + z**2)
    if R > 0:
        theta0 = math.acos(z / R)
        theta = -(math.pi/2 - theta0)
        sin_theta0 = math.sin(theta0)
        phi0 = math.acos(x / R / sin_theta0) if sin_theta0 != 0 else math.pi/2
        phi = -(math.pi/2 - phi0)
        psi = 0.0
        # print(f"{x}, {y}, {z}: {theta0=}, {theta=}, {sin_theta0=}, {phi0=}, {phi=}")
    else:
        theta = 0.0
        phi = 0.0
        psi = 0.0
    return theta, phi, psi


def _get_old_angles(x: float, y: float, z: float) -> tp.Tuple[float, float]:
    R = math.sqrt(x**2 + y**2 + z**2)
    if R == 0:
        return 0.0, 0.0

    Va = -np.array([x / R, y / R, z / R])
    V0 = np.array([0., -1., 0.])
    print(f"{Va=}")

    e3 = Va
    s_ = np.sqrt(e3[0]**2 + e3[1]**2)
    print(f"{s_=}")
    C = e3[2] / s_
    print(f"{C=}")
    e1 = np.array([C*e3[0], C*e3[1], -s_])
    e2 = np.cross(e1, e3)
    print(f"{e1=}")
    print(f"{e2=}")

    cos_theta_rot = e3 @ V0
    Dx = e1 @ V0
    Dy = e2 @ V0
    print(f"{Dx=}, {Dy=}")
    cos_phi_rot = Dx / np.sqrt(Dx**2 + Dy**2) if Dx > 0 and Dy > 0 else 1
    theta_rot = -np.acos(cos_theta_rot)
    phi_rot = np.acos(cos_phi_rot)

    return theta_rot, phi_rot


def _convert_angles_to_old(theta: float, phi: float) -> tp.Tuple[float, float]:
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    cos_phi = np.cos(phi)
    # sin_phi = np.sin(phi)
    cos_theta_1 = cos_theta * cos_phi
    sin_theta_1 = np.sin(np.acos(cos_theta_1))
    cos_phi_1 = sin_theta / sin_theta_1 if sin_theta_1 != 0 else 1

    return np.acos(cos_theta_1), np.acos(cos_phi_1)


def _sets_det_coordinate(input_filename: str, distance: float, x_shift: float, z_shift,
                         output_filename: str, indent: bool = False, set_angles: bool = False,
                         is_old_angles: bool = False):
    with open(input_filename) as f:
        data = json.load(f)

    # det height
    det_center = _calc_distance_from_cap_to_crystal_center(data["Detector"])

    # source width
    source_width = _calc_source_half_width(data["ContainerSource"])

    det_y_coord = source_width + distance + det_center

    # set to output file
    data["ContainerSource"]["DetectorPosition"]["detX"] = x_shift
    data["ContainerSource"]["DetectorPosition"]["detY"] = det_y_coord
    data["ContainerSource"]["DetectorPosition"]["detZ"] = z_shift

    # set angles to output file
    if set_angles:
        theta, phi, psi = _get_angles(x_shift, det_y_coord, z_shift)
        if is_old_angles:
            theta_old, phi_old = _convert_angles_to_old(theta, phi)
            data["ContainerSource"]["DetectorPosition"]["detTheta"] = theta_old
            data["ContainerSource"]["DetectorPosition"]["detPhi"] = phi_old
        else:
            data["ContainerSource"]["DetectorPosition"]["detTheta"] = theta
            data["ContainerSource"]["DetectorPosition"]["detPhi"] = phi
            data["ContainerSource"]["DetectorPosition"]["detPsi"] = psi


    indent = 4 if indent else None
    with open(output_filename, 'w') as g:
        json.dump(data, g, indent=indent)


@register_operation
class SetEffMakerDistanceOperation:
    """
    SetEffMakerDistanceOperation converts detector-object distance to detector coordinates
        and sets it to physspec_input.json
    parameters:
        input_filename: physspec_input.json
        output_filename: physspec_input.json
        distance: distance from source to detector (from side to cap)
        detector_xshift: detector x coordinate
        detector_zshift: detector z coordinate
        to_indent_output: add spaces and new lines to output json
        set_angles: if set set_angles, angles also be calculated
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.distance = 0.0
        self.detector_xshift = 0.0
        self.detector_zshift = 0.0
        self.to_indent_output = False
        self.set_angles = False
        self.is_old_angles = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'SetEffMakerDistanceOperation'):
        op = SetEffMakerDistanceOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.distance = section["distance"]
        op.detector_xshift = section.get('detector_xshift', op.detector_xshift)
        op.detector_zshift = section.get('detector_zshift', op.detector_zshift)
        op.to_indent_output = section.get('to_indent_output', op.to_indent_output)
        op.set_angles = section.get('set_angles', op.set_angles)
        op.is_old_angles = section.get('is_old_angles', op.is_old_angles)
        return op

    def run(self) -> None:
        print('start set effmaker distance')
        _sets_det_coordinate(self.input_filename, self.distance, self.detector_xshift,
                             self.detector_zshift, self.output_filename, self.to_indent_output,
                             self.set_angles, self.is_old_angles)
