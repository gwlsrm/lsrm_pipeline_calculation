"""
parser for lsrm efa-files
"""
import math
import typing as tp


LN_10 = 2.30259  # ln(10)


def poly_reverse(x: float, poly_coeffs: tp.List[float]) -> float:
    assert len(poly_coeffs) > 0
    res = 0
    for c in poly_coeffs:
        res = res * x + c
    return res


def linear_interpol(xl: float, yl: float, xr: float, yr: float, x: float) -> float:
    assert xl < xr
    w = (x - xl) / (xr - xl)
    return (1 - w) * yl + w * yr


class EffPoint:
    """
    EffPoint -- class with calibration data for efficiency calibration
    """
    def __init__(self, energy: float, eff: float, deff: float, nuclide: str, area: float,
                 darea: float, intens: float):
        self.energy = energy
        self.eff = eff
        self.deff = deff
        self.nuclide = nuclide
        self.area = area
        self.darea = darea
        self.intens = intens

    def __repr__(self) -> str:
        return f"{self.energy}={self.eff},{self.deff},{self.nuclide},{self.area},{self.darea}," + \
            f"{self.intens}"

    @staticmethod
    def parse_from_string(line: str) -> "EffPoint":
        # 39.523=5.399922E-04,1.649,Eu-152,195877,1220,20.8
        words = line.split('=')
        if len(words) != 2:
            raise RuntimeError(
                "Bad EffPoint format, expected energy=eff,deff,nuclide,area,darea,intense" +
                f", but got {line} -- no '=' in line")
        energy = float(words[0])

        words = words[1].split(',')
        if len(words) < 6:
            raise RuntimeError(
                "Bad EffPoint format, expected energy=eff,deff,nuclide,area,darea,intense" +
                f", but got {line} -- not enough fields")
        eff = float(words[0])
        deff = float(words[1])
        nuclide = words[2]
        area = float(words[3])
        darea = float(words[4])
        intens = float(words[5])
        return EffPoint(energy, eff, deff, nuclide, area, darea, intens)


class EffZone:
    """
    EffZone -- class for efficiency calibration zone
    """
    def __init__(self, degree: int, left: float, right: float, deviation: float,
                 main_poly_coeffs: tp.Optional[tp.List[float]] = None,
                 orth_polys_coeffs: tp.Optional[tp.List[tp.List[float]]] = None):
        self.degree = degree
        self.left = left  # log10(left energy bound)
        self.right = right  # log10(right energy bound)
        self.deviation = deviation
        self.orth_polys_coeffs = orth_polys_coeffs or []
        self.main_poly_coeffs = main_poly_coeffs or []

    def contain_energy(self, log_energy: float) -> bool:
        return self.left <= log_energy <= self.right

    def calc_efficiency(self, log_energy: float) -> tp.Tuple[float, float]:
        eff = 0
        deff = 0
        for main_coeff, polys in zip(self.main_poly_coeffs, self.orth_polys_coeffs):
            y_value = poly_reverse(log_energy, polys)
            eff += main_coeff * y_value
            deff += (y_value)**2
        deff = math.sqrt(deff) * LN_10 * self.deviation
        return eff, deff

    def __str__(self) -> str:
        return f"Zone: {self.degree}, {10**(self.left)}, {10**(self.right)}, {self.deviation}"

    def print_zone(self, num: int) -> str:
        num += 1
        res = f"Zone_{num}={self.degree},{self.left},{self.right},{self.deviation}\n"
        for i, pol in enumerate(self.orth_polys_coeffs):
            res += f"Curve_{num}_{i+1}="
            res += ",".join(str(coef) for coef in pol)
            res += '\n'
        res += f"Curve_{num}=" + ",".join(str(coef) for coef in self.main_poly_coeffs) + "\n"
        return res

    @staticmethod
    def parse_from_line(line: str) -> "EffZone":
        # Zone_num=degree,log10_left,log10_right,deviation
        # Zone_1=5,1.43437301082,2.45410566518,0.00215692872
        words = line.split('=')
        if len(words) != 2:
            raise RuntimeError(
                "Bad Zone format, expected Zone_n=degree,left,right,deviation" +
                f", but got {line} -- no '=' in line")

        words = words[1].split(',')
        if len(words) != 4:
            raise RuntimeError(
                "Bad Zone format, expected Zone_n=degree,left,right,deviation" +
                f", but got {line} -- -- not enough fields")

        degree = int(words[0])
        left = float(words[1])
        right = float(words[2])
        deviation = float(words[3])
        return EffZone(degree, left, right, deviation)

    @staticmethod
    def parse_poly_from_line(line: str) -> tp.Tuple[int, int, tp.List[float]]:
        # Curve_1_2=.783904515E+2,-.154763032E+3
        # Curve_1=-.156491110E+1,.436638669E-1
        words = line.split('=')
        if len(words) != 2:
            raise RuntimeError(
                "Bad Curve format, expected Curve_n[_m]=c[0],c[1],..." +
                f", but got {line} -- no '=' in line")

        coeffs = [float(w) for w in words[1].split(',')]
        words = words[0].split('_')
        zone_num = int(words[1])
        if len(words) == 2:  # main poly
            degree = 0
        else:   # orth poly
            degree = int(words[2])
        return zone_num, degree, coeffs


class Efficiency:
    """
    Efficiency -- class for efficiency calibration
    """
    def __init__(self, record_name: str = "",
                 header_lines: tp.Optional[tp.List[tp.Tuple[str, str]]] = None,
                 eff_points: tp.Optional[tp.List[EffPoint]] = None,
                 zones: tp.Optional[tp.List[EffZone]] = None):
        self.record_name = record_name
        self.header_lines = header_lines or []
        self.points = eff_points or []
        self.zones = zones or []

    def get_nuclides(self) -> tp.List[str]:
        nuclides = set()
        for p in self.points:
            nuclides.add(p.nuclide)
        return list(nuclides)

    def get_eff(self, energy: float) -> tp.Tuple[float]:
        assert energy > 0
        assert len(self.zones) > 0
        energy = math.log10(energy)
        # cases:
        # lefter 1st zone
        # righter last zone
        # inside 1 zone
        # inside 2 zones intersection
        # between 2 zones
        if energy < self.zones[0].left:
            eff, deff = self.zones[0].calc_efficiency(energy)
        elif energy > self.zones[-1].right:
            eff, deff = self.zones[-1].calc_efficiency(energy)
        else:
            lidx = 0
            while lidx < len(self.zones) and self.zones[lidx].right < energy:
                lidx += 1
            ridx = lidx+1

            if energy < self.zones[lidx].left:
                # between
                assert lidx > 0
                eff_left, deff_left = self.zones[lidx-1].calc_efficiency(energy)
                eff_right, deff_right = self.zones[lidx].calc_efficiency(energy)
                eff = linear_interpol(self.zones[lidx-1].right, eff_left,
                                      self.zones[lidx].left, eff_right, energy)
                deff = linear_interpol(self.zones[lidx-1].right, deff_left,
                                       self.zones[lidx].left, deff_right, energy)
            elif ridx == len(self.zones):  # last zone
                # inside
                eff, deff = self.zones[lidx].calc_efficiency(energy)
            elif self.zones[ridx].left < energy:
                # overlap
                eff_left, deff_left = self.zones[lidx].calc_efficiency(energy)
                eff_right, deff_right = self.zones[ridx].calc_efficiency(energy)
                eff = linear_interpol(self.zones[ridx].left, eff_right,
                                      self.zones[lidx].right, eff_left, energy)
                deff = linear_interpol(self.zones[ridx].left, deff_right,
                                       self.zones[lidx].right, deff_left, energy)
            else:
                # inside
                eff, deff = self.zones[lidx].calc_efficiency(energy)

        return 10**(eff), deff

    def get_energy_range_kev(self) -> tp.List[float]:
        if self.zones:
            return [10**(self.zones[0].left), 10**(self.zones[-1].right)]
        else:
            return [self.points[0].energy, self.points[-1].energy]

    def __repr__(self) -> str:
        return "Efficiency: " + self.record_name +\
              f": with {len(self.points)} points and {len(self.zones)} zones"

    def save_as_efr(self, filename: str) -> None:
        with open(filename, 'w') as f:
            f.write(self.record_name + '\n')
            for n, v in self.header_lines:
                f.write(n + '=' + v + '\n')
            for p in self.points:
                f.write(str(p) + '\n')

    def convert_records_to_efa(self) -> None:
        # record name
        tokens = self.record_name.split(';')
        if len(tokens) != 3:
            return
        assert len(tokens) == 3
        self.record_name = ';'.join([tokens[0], tokens[1]+']'])
        # headers
        nuclide = tokens[2][:-1]
        self.header_lines = [(n, v) for n, v in self.header_lines if n != nuclide]

    def convert_records_to_efr(self, nuclide: str) -> None:
        # record name
        tokens = self.record_name.split(';')
        if len(tokens) == 3:
            return
        assert len(tokens) == 2
        self.record_name = self.record_name[:-1] + ";" + nuclide + "]"
        # headers
        self.header_lines.append((nuclide, "100,1,1"))

    def save_as_efa(self, filename: str, is_append: bool = False) -> None:
        self.convert_records_to_efa()
        mode = 'a' if is_append else 'w'
        with open(filename, mode) as f:
            if mode == 'a':
                f.write('\n')
            f.write(self.record_name + '\n')
            for n, v in self.header_lines:
                f.write(n + '=' + v + '\n')
            for p in self.points:
                f.write(str(p) + '\n')
            f.write(f"Zones={len(self.zones)}\n")
            for i, zone in enumerate(self.zones):
                f.write(zone.print_zone(i))


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _is_section_name(line: str) -> bool:
    return line.startswith('[') and line.endswith(']') and line != "[MaterialsDescription]"


def _get_efficiency_from_file(f: tp.TextIO, line_num: int = 0) -> tp.Optional[Efficiency]:
    eff_points: tp.List[EffPoint] = []
    zones: tp.List[EffZone] = []
    header_lines: tp.List[tp.Tuple[str, str]] = []
    # read file
    is_start = False
    is_header = False
    is_data = False
    # go to line_num
    for _ in range(line_num):
        if not f.readline():
            return None

    record_name = None
    for line in f:
        line = line.strip()

        # start of section
        if not is_start and _is_section_name(line):
            is_start = True
            is_header = True
            record_name = line
            continue

        # end of section
        if is_start and (not line or _is_section_name(line)):
            break

        # section reading
        words = line.split('=')
        if len(words) < 2:
            continue

        # header lines
        if is_header:
            if _is_float(words[0]):
                is_header = False
                is_data = True
            else:
                header_lines.append((words[0], words[1]))
        # end of header lines

        # data start
        if is_data:
            if words[0] == "Zones":
                is_data = False
            else:
                eff_points.append(EffPoint.parse_from_string(line))
                continue
        # data end

        # zones
        if words[0].startswith("Zone_"):
            zones.append(EffZone.parse_from_line(line))
        elif words[0].startswith("Curve"):
            zone_num, poly_deg, coeffs = EffZone.parse_poly_from_line(line)
            if poly_deg:
                zones[zone_num-1].orth_polys_coeffs.append(coeffs)
            else:
                zones[zone_num-1].main_poly_coeffs = coeffs
    if record_name is not None:
        return Efficiency(record_name, header_lines, eff_points, zones)


def get_efficiency_from_efa(filename: str, line_num: int = 0) -> tp.Optional[Efficiency]:
    """
    get_efficiency_from_efa parses *.efa file and returns first efficiency record or record,
        placed on line number line_num
    """
    with open(filename, 'r', encoding='cp1251') as f:
        return _get_efficiency_from_file(f, line_num=line_num)


def get_eff_by_name(filename: str, record_name: str) -> tp.Optional[Efficiency]:
    """
    get_eff_by_name parses efa-file and returns Efficiency from it by record name (line in "[]")
    """
    eff_lst = get_eff_records_from_efa(filename)
    if record_name not in eff_lst:
        return None
    return get_efficiency_from_efa(filename, eff_lst[record_name])


def get_eff_records_from_efa(filename: str) -> tp.Dict[str, int]:
    """
    get_eff_records_from_efa returns efficiency to line number, where it is in file
    """
    efficiency_to_linenum: tp.Dict[str, int] = {}
    with open(filename, 'r', encoding="cp1251") as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if _is_section_name(line):
                efficiency_to_linenum[line] = line_num
    return efficiency_to_linenum


def get_all_efficiencies_from_efa(filename: str) -> tp.Dict[str, Efficiency]:
    """
    get all efficiencies from *.efa or *.efr file
    """
    efficiencies: tp.Dict[str, Efficiency] = {}
    with open(filename, 'r', encoding="cp1251") as f:
        for _ in range(1000):
            eff = _get_efficiency_from_file(f)
            if not eff:
                break
            efficiencies[eff.record_name] = eff
    return efficiencies


def main():
    eff_list = get_eff_records_from_efa("test.efa")
    print("list of efficiencies:")
    for name, line_num in eff_list.items():
        print(f"{name}: {line_num}")

    eff = get_efficiency_from_efa("test.efa")
    print(f"Found {len(eff.points)} eff points")
    for p in eff.points:
        print(p.energy, "=", p.eff, p.deff, p.nuclide)
    print(f"Found {len(eff.zones)} zones")
    for z in eff.zones:
        print(z.degree, 10**(z.left), 10**(z.right), z.deviation)
        print(z.main_poly_coeffs)
        print(z.orth_polys_coeffs)


if __name__ == "__main__":
    main()
