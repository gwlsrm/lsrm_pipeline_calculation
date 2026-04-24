import typing as tp


def calc_distance_from_cap_to_crystal_center(
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


def calc_source_half_width(source_data: tp.Dict[str, tp.Any]) -> float:
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
