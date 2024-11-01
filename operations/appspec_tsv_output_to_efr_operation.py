import json
import os
import math
import typing as tp

from operations.operation_registry import register_operation


EPS = 1e-15
NOT_ESSENTIAL = "not essential"
JsonObject = tp.Dict[str, tp.Any]

def _parse_tsv_output(filename: str) -> tp.Dict[str, tp.List[float]]:
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
    return res


def _find_cell_with_source(data: JsonObject) -> tp.Optional[JsonObject]:
    source_cell = None
    for cell in data["ContainerSource"]["Cells"]:
        if cell.get("RadioactiveSource"):
            if source_cell is None:
                source_cell = cell
            else:
                return None
    return source_cell


def _get_volume(cell: tp.Optional[JsonObject]) -> tp.Optional[int]:
    if not cell:
        return None
    shape = cell["Shape"]
    dims = cell["Dimensions"]
    if shape in ("CylZ", "CylX", "CylY"):
        h = dims["Dim1"]
        r = dims["Dim2"]
        return int(h * math.pi * r**2)
    elif shape == "Sphere":
        return int(4/3 * math.pi * dims["Dim1"]**3)
    elif shape == "Cuboid":
        return int(dims["Dim1"] * dims["Dim2"] * dims["Dim3"])
    elif shape in ("ConeZ", "ConeX", "ConeY"):
        h = dims["Dim1"]
        r1 = dims["Dim2"]
        r2 = dims["Dim3"]
        return int(1/3 * math.pi * h * (r1**2 + r1*r2 + r2**2))
    else:
        raise RuntimeError("Unknown cell shape " + shape)


def _convert_material_to_lsrm(material: JsonObject) -> JsonObject:
    res = {
        "Name": material["Name"],
        "Ro": material["rho"],
        "Compound": [{str(e["z"]): e["frac"]} for e in material["elements"]],
    }
    return res


def _get_material(cell: tp.Optional[tp.Dict[str, tp.Any]]) -> str:
    if not cell:
        return NOT_ESSENTIAL
    material = cell["Material"]
    material_lsrm = _convert_material_to_lsrm(material)
    return json.dumps(material_lsrm)


def _get_rho(cell : tp.Optional[JsonObject]) -> tp.Optional[float]:
    if not cell:
        return None
    return cell["Material"]["rho"]


def _get_det_geom_params_from_physspec_input(
        filename: str) -> tp.Tuple[str, str, tp.Optional[int], str, tp.Optional[float]]:
    with open(filename) as f:
        data = json.load(f)
    det_name = data["Detector"].get("Name", "")
    geom_name = data["ContainerSource"]["Name"]
    cell_with_source = _find_cell_with_source(data)
    volume = _get_volume(cell_with_source)
    material = _get_material(cell_with_source)
    rho = _get_rho(cell_with_source)
    return det_name, geom_name, volume, material, rho


def _save_to_efr(eff_result: tp.Dict[str, tp.List[float]],
                 detector_name: str, geometry: str, distance: tp.Optional[float],
                 volume: tp.Optional[float], material: str, density: tp.Optional[float],
                 other_params: tp.Dict[str, tp.Any],
                 output_filename: str):
    with open(output_filename, 'w') as f:
        # header
        f.write(f"[{detector_name};{geometry};Nuclide]\n")
        f.write(f"Detector={detector_name}\n")
        f.write(f"Geometry={geometry}\n")
        f.write(f"Volume,ml={volume if volume else NOT_ESSENTIAL}\n")
        f.write(f"Density,g/cm3={density if density else NOT_ESSENTIAL}\n")
        f.write(f"Material={material}\n")
        f.write("Thick,mm=0\n")
        f.write("DThick,mm=0\n")
        f.write(f"Distance,cm={distance}\n")
        for k, v in other_params.items():
            f.write(f"{k}={v}\n")
        f.write("CorrectionFile=\n")
        f.write("Nuclide=100,1,1\n")
        # efficiency data
        n = len(eff_result["energy"])
        for i in range(n):
            e = eff_result["energy"][i]
            eff = eff_result["efficiency"][i]
            eff = max(eff, EPS)
            deff_rel = eff_result["defficiency"][i] / eff * 100
            intensity = eff_result["intensity"][i]
            cr = eff_result["count_rate"][i]
            f.write(f"{e*1000}={eff},{deff_rel},Nuclide,{cr},1,{intensity}\n")


@register_operation
class AppspecTsvOutputToEfr:
    """
    AppspecTsvOutputToEfr converts appspec output tsv-file to efr-file
    All needed information like detector_name, geometry_name, volume, material, rho
    it can take from physspec_input_filename or you can pass them directly in operation parameters.
    distance can be set only directly through operation parameters
    Also you can any other prams in form {param_name: param_value, ...}
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.physspec_input_filename = ""
        self.detector_name = ""
        self.geometry_name = ""
        self.distance = 0.0
        self.volume = None
        self.material = None
        self.density = None
        self.other_params = {}

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'AppspecTsvOutputToEfr':
        op = AppspecTsvOutputToEfr()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.physspec_input_filename = os.path.join(project_dir, section['physspec_input_filename'])
        op.detector_name = section.get("detector_name", op.detector_name)
        op.geometry_name = section.get("geometry_name", op.geometry_name)
        op.distance = section.get("distance", op.distance)
        op.volume = section.get("volume", op.volume)
        op.material = section.get("material", op.material)
        op.density = section.get("density", op.density)
        op.other_params = section.get("other_params", op.other_params)
        return op

    def run(self) -> None:
        print('start appspec_tsv_output_to_efr')
        eff_result = _parse_tsv_output(self.input_filename)
        if self.physspec_input_filename:
            det_name, geom_name, volume, material, density = _get_det_geom_params_from_physspec_input(
                self.physspec_input_filename)
            self.detector_name = self.detector_name or det_name
            self.geometry_name = self.geometry_name or geom_name
            self.volume = self.volume or volume
            self.material = self.material or material or NOT_ESSENTIAL
            self.density = self.density or density

        _save_to_efr(eff_result,
                     self.detector_name, self.geometry_name, self.distance, self.volume,
                     self.material, self.density, self.other_params,
                     self.output_filename)
