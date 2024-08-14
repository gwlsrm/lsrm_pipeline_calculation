"""
parser for lsrm efa-files
"""
import math


class EffPoint:
    def __init__(self, energy, eff, deff, nuclide, area, darea, intens):
        self.energy = energy
        self.eff = eff
        self.deff = deff
        self.nuclide = nuclide
        self.area = area
        self.darea = darea
        self.intens = intens

    def __repr__(self):
        return f"{self.energy}={self.eff},{self.deff},{self.nuclide},{self.area},{self.darea}," + \
            f"{self.intens}"

    @staticmethod
    def parse_from_string(line):
        # 39.523=5.399922E-04,1.649,Eu-152,195877,1220,20.8
        words = line.split('=')
        if len(words) != 2:
            return None
        energy = float(words[0])
        words = words[1].split(',')
        if len(words) < 6:
            return None
        eff = float(words[0])
        deff = float(words[1])
        nuclide = words[2]
        area = float(words[3])
        darea = float(words[4])
        intens = float(words[5])
        return energy, eff, deff, nuclide, area, darea, intens


class OrthPoly:
    def __init__(self, orth_polys_coeffs, main_poly_coeffs):
        self.orth_polys_coeffs = orth_polys_coeffs
        self.main_poly_coeffs = main_poly_coeffs


class EffZone:
    def __init__(self, degree, left, right, deviation, main_poly_coeffs, orth_polys_coeffs):
        self.degree = degree
        self.left = left
        self.right = right
        self.deviation = deviation
        self.orth_polys_coeffs = orth_polys_coeffs
        self.main_poly_coeffs = main_poly_coeffs

    def __str__(self):
        return f"{self.left} {self.right} {self.degree}"

    def print_zone(self, num):
        num += 1
        res = f"Zone_{num}={self.degree},{math.log10(self.left)},{math.log10(self.right)}\n"
        for i, pol in enumerate(self.orth_polys_coeffs):
            res += f"Curve_{num}_{i}="
            res += ",".join(str(coef) for coef in pol)
            res += '\n'
        res += f"Curve_{num}=" + ",".join(str(coef) for coef in self.main_poly_coeffs) + "\n"
        return res

    @staticmethod
    def parse_from_line(line):
        # Zone_1=5,1.43437301082,2.45410566518,0.00215692872
        words = line.split('=')
        if len(words) != 2:
            return None
        words = words[1].split(',')
        if len(words) < 4:
            return None
        degree = int(words[0])
        left = 10**float(words[1])
        right = 10**float(words[2])
        deviation = float(words[3])
        return degree, left, right, deviation

    @staticmethod
    def parse_curve_from_line(line):
        # .783904515E+2,-.154763032E+3
        return [float(w) for w in line.split(',')]

    @staticmethod
    def is_curve_line(line):
        # Curve_1_2=.783904515E+2,-.154763032E+3
        # Curve_1=-.156491110E+1,.436638669E-1
        return line.startswith("Curve_")

    @staticmethod
    def parse_poly_from_line(line):
        words = line.split('=')
        if len(words) < 2:
            return None
        coeffs = EffZone.parse_curve_from_line(words[1])
        words = words[0].split('_')
        zone_num = int(words[1])
        if len(words) == 2:  # main poly
            degree = 0
        else:   # orth poly
            degree = int(words[2])
        return zone_num, degree, coeffs


class Efficiency:
    def __init__(self, header="", header_lines=None, eff_points=None, zones=None):
        if eff_points is None:
            eff_points = []
        if zones is None:
            zones = []
        if header_lines is None:
            header_lines = []
        self.header = header
        self.header_lines = header_lines
        self.points = eff_points
        self.zones = zones

    def get_nuclides(self):
        nuclides = []
        for p in self.points:
            if p.nuclide not in nuclides:
                nuclides.append(p.nuclide)
        return nuclides

    def get_eff(self, energy):
        if not self.zones:
            return 0

    def __repr__(self):
        return "Efficiency: " + self.header +\
              f": with {len(self.points)} points and {len(self.zones)} zones"

    def save_as_efr(self, filename):
        with open(filename, 'w') as f:
            f.write(self.header + '\n')
            for n, v in self.header_lines:
                f.write(n + '=' + v + '\n')
            for p in self.points:
                f.write(str(p) + '\n')

    def save_as_efa(self, filename):
        with open(filename, 'w') as f:
            f.write(self.header + '\n')
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


def get_efficiency_from_efa(filename, line_num=0):
    eff_points = []
    zones = []
    header_lines = []
    with open(filename, 'r') as f:
        is_start = False
        is_header = False
        is_data = False
        # go to line_num
        for _ in range(line_num):
            if not f.readline():
                break

        for line in f:
            line = line.strip()

            # start of section
            if not is_start and line and line[0] == '[':
                is_start = True
                is_header = True
                header = line
                continue
            # end of section

            if is_start and (not line or line == ' ' or line[0] == '['):
                break
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
            # end header lines

            # data start
            if is_data:
                if words[0] == "Zones":
                    is_data = False
                else:
                    t = EffPoint.parse_from_string(line)
                    if t:
                        eff_points.append(EffPoint(*t))
                    else:
                        print("cannot parse data line:", line)
                    continue
            # data end
            # zones
            if words[0].startswith("Zone_"):
                t = EffZone.parse_from_line(line)
                if t:
                    zones.append(EffZone(*t, [], []))
            elif words[0].startswith("Curve"):
                t = EffZone.parse_poly_from_line(line)
                if not t:
                    continue
                zone_num, poly_deg, coeffs = t[0], t[1], t[2]
                if poly_deg:
                    zones[zone_num-1].orth_polys_coeffs.append(coeffs)
                else:
                    zones[zone_num-1].main_poly_coeffs = coeffs
    return Efficiency(header, header_lines, eff_points, zones)


def get_eff_by_num(filename, num):
    eff_lst = get_eff_list_from_efa(filename)
    if num >= len(eff_lst):
        return None
    return get_efficiency_from_efa(filename, eff_lst[num].line_num)


def get_eff_by_name(filename, name):
    eff_lst = get_eff_list_from_efa(filename)
    line_num = -1
    for eff_rec in eff_lst:
        if name == eff_rec.header:
            line_num = eff_rec.line_num
            break
    if line_num == -1:
        return None
    return get_efficiency_from_efa(filename, line_num)


class EfaRecord:
    def __init__(self, header, line_num):
        self.header = header
        self.line_num = line_num

    def __repr__(self):
        return self.header


def get_eff_list_from_efa(filename):
    eff_list = []
    line_num = 0
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('['):
                eff_list.append(EfaRecord(line, line_num))
            line_num += 1
    return eff_list


if __name__ == "__main__":
    eff = get_efficiency_from_efa("test.efa")
    print(f"Found {len(eff.points)} eff points")
    for p in eff.points:
        print(p.energy, "=", p.eff, p.deff, p.nuclide)
    print(f"Found {len(eff.zones)} zones")
    for z in eff.zones:
        print(z.degree, z.left, z.right)
        print(z.main_poly_coeffs)
        print(z.orth_polys_coeffs)
