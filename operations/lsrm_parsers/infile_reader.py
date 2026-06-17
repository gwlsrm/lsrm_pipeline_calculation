"""
    Parse lsrm in-files
"""

from ..common_parsers.config_parser import ConfigFileParser
from .constants import *


class InFileReader(ConfigFileParser):
    def get_float_with_cm(self, key):
        value = self.get(key, default=0)
        if value:
            value = float(value.split()[0])
        return value

    def get_material(self, mat_name, prefix):
        elements_count_key = f"{prefix}n{mat_name}Elements"
        if elements_count_key not in self.data:
            elements_count_key = f"{prefix}n{mat_name}"
        elements_count = self.get(elements_count_key, cast_type=int)
        if not elements_count:
            raise RuntimeError(f"Invalid material {mat_name} with 0 elements count")
        rho = self.get(f"{prefix}Ro{mat_name}", cast_type=float)
        if rho < 0:
            raise RuntimeError(f"Material {mat_name} rho cannot be negative: {rho}")
        fraction_type = self.get(f"{prefix}FractionType{mat_name}", default="MASS")
        elements = []
        for i in range(elements_count):
            z = self.get(f"{prefix}Z{mat_name}[{i}]", cast_type=int)
            frac = self.get(f"{prefix}Fractions{mat_name}[{i}]", cast_type=float)
            elements.append({'z': z, 'frac': frac})
        return {'rho': rho, 'fraction_type': fraction_type, 'elements': elements}


    def get_file_type(self):
        if 'DetectorType' in self.data:
            return self.get('DetectorType')
        elif 'SourceType' in self.data:
            return self.get('SourceType')
        elif 'AN_Name' or 'AN_kev_per_ch' in self.data:
            return 'ANALYZER'
        else:
            raise RuntimeError(f'Unknown file type for file: {self.filename}')


def get_object_type(file_type):
    if file_type in ['COAXIAL', 'SCINTILLATOR', 'COAX_WELL']:
        return 'Detector'
    elif file_type in ['POINT', 'CYLINDER', 'MARINELLI', 'CONE']:
        return 'Source'
    elif file_type == 'ANALYZER':
        return 'Analyzer'


def parse_geometry(parser, file_type):
    prefix = FILE_TYPE_TO_PREFIX[file_type]
    return {geom_name: parser.get_float_with_cm(prefix+geom_name) for geom_name in FILE_TYPE_TO_GEOM_NAME[file_type]}


def parse_material(parser, file_type):
    prefix = FILE_TYPE_TO_PREFIX[file_type]
    return {mat_name: parser.get_material(mat_name, prefix) for mat_name in FILE_TYPE_TO_MAT_NAME[file_type]}


def parse_anal_params(parser):
    prefix = 'AN_';
    return {
        'Name': parser.get(prefix+'Name'),
        'FWHM_122': parser.get(prefix+'FWHM_122', cast_type=float),
        'FWHM_662': parser.get(prefix+'FWHM_662', cast_type=float),
        'FWHM_1332': parser.get(prefix+'FWHM_1332', cast_type=float),
        'kev_per_ch': parser.get(prefix+'kev_per_ch', cast_type=float),
        'N_ch': parser.get(prefix+'N_ch', cast_type=int),
    }
