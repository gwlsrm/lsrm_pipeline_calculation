import os
import typing as tp

from operations.operation_registry import register_operation


EPS = 1e-15


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


def _save_to_efr(eff_result: tp.Dict[str, tp.List[float]],
                 detector_name: str, geometry: str, output_filename: str):
    with open(output_filename, 'w') as f:
        # header
        f.write(f"[{detector_name};{geometry};Nuclide]\n")
        f.write(f"Detector={detector_name}\n")
        f.write(f"Geometry={geometry}\n")
        f.write("Volume,ml=not essential\n")
        f.write("Density,g/cm3=not essential\n")
        f.write("Material=not essential\n")
        f.write("Thick,mm=0\n")
        f.write("DThick,mm=0\n")
        f.write("Distance,cm=0\n")
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
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.detector_name = "Detector"
        self.geometry = "Geometry"

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'AppspecTsvOutputToEfr':
        op = AppspecTsvOutputToEfr()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.detector_name = section.get("detector_name", op.detector_name)
        op.geometry = section.get("geometry", op.geometry)
        return op

    def run(self) -> None:
        print('start appspec_tsv_output_to_efr')
        eff_result = _parse_tsv_output(self.input_filename)

        _save_to_efr(eff_result,
                     self.detector_name, self.geometry, self.output_filename)
