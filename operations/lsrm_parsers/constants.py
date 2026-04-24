COAXIAL_GEOM_NAMES = [
    'CrystalDiameter',
    'CrystalHeight',
    'CrystalHoleDiameter',
    'CrystalHoleHeight',
    'CrystalFrontDeadLayer',
    'CrystalSideDeadLayer',
    'CrystalBackDeadLayer',
    'CrystalHoleBottomDeadLayer',
    'CrystalHoleSideDeadLayer',
    'CrystalSideCladdingThickness',
    'CapToCrystalDistance',
    'DetectorCapDiameter',
    'DetectorCapFrontThickness',
    'DetectorCapSideThickness',
    'DetectorCapBackThickness',
    'DetectorMountingThickness',
    'CrystalCurvatureRadius',
]

SCINTIL_GEOM_NAMES = [
    'CrystalDiameter',
    'CrystalHeight',
    'CrystalFrontReflectorThickness',
    'CrystalSideReflectorThickness',
    'CrystalFrontCladdingThickness',
    'CrystalSideCladdingThickness',
    'DetectorFrontPackagingThickness',
    'DetectorSidePackagingThickness',
    'DetectorFrontCapThickness',
    'DetectorSideCapThickness',
    'DetectorMountingThickness',
]

COAX_WELL_GEOM_NAMES = [
    'CrystalDiameter',
    'CrystalHeight',
    'CrystalHoleDiameter',
    'CrystalHoleHeight',
    'CrystalFrontDeadLayer',
    'CrystalSideDeadLayer',
    'CrystalBackDeadLayer',
    'CrystalHoleBottomDeadLayer',
    'CrystalHoleSideDeadLayer',
    'CrystalSideCladdingThickness',
    'CapToCrystalDistance',
    'DetectorCapDiameter',
    'DetectorCapFrontThickness',
    'DetectorCapSideThickness',
    'DetectorCapBackThickness',
    'DetectorCapHoleDiameter',
    'DetectorCapHoleHeight',
    'DetectorCapHoleBottomThickness',
    'DetectorCapHoleSideThickness',
    'DetectorMountingThickness',
]

POINT_GEOM_NAMES = [
    'pdistance',
    'prho',
]

CYL_GEOM_NAMES = [
    'BeakerToDetectorFrontDistance',
    'BeakerDiameter',
    'BeakerHeight',
    'BeakerSideWallThickness',
    'BeakerEndWallThickness',
    'SourceHeight',
]

MAR_GEOM_NAMES = [
    'BeakerToDetectorFrontDistance',
    'BeakerDiameter',
    'BeakerHeight',
    'BeakerHoleDiameter',
    'BeakerHoleHeight',
    'BeakerSideThickness',
    'BeakerEndWallThickness',
    'BeakerHoleSideThickness',
    'BeakerHoleEndWallThickness',
    'SourceHeight',
]

CONE_GEOM_NAMES = [
    'BeakerToDetectorFrontDistance',
    'BeakerDiameterBottom',
    'BeakerDiameterTop',
    'BeakerHeight',
    'BeakerSideWallThickness',
    'BeakerEndWallThickness',
    'SourceHeight',
]

FILE_TYPE_TO_GEOM_NAME = {
    'COAXIAL': COAXIAL_GEOM_NAMES,
    'SCINTILLATOR': SCINTIL_GEOM_NAMES,
    'COAX_WELL': COAX_WELL_GEOM_NAMES,
    'POINT': POINT_GEOM_NAMES,
    'CYLINDER': CYL_GEOM_NAMES,
    'MARINELLI': MAR_GEOM_NAMES,
    'CONE': CONE_GEOM_NAMES,
}

COAXIAL_MAT_NAMES = [
    'Crystal',
    'CrystalSideCladding',
    'CrystalMounting',
    'DetectorCap',
    'Vacuum',
]

SCINIL_MAT_NAMES = [
    'Crystal',
    'CrystalCladding',
    'CrystalReflector',
    'DetectorPackaging',
    'DetectorCap',
]

COAX_WELL_MAT_NAMES = [
    'Crystal',
    'CrystalSideCladding',
    'CrystalMounting',
    'DetectorCap',
    'Vacuum',
]

CYL_MAT_NAMES = [
    'Wall',
    'Source',
    'EmptySpace',
]

MAR_MAT_NAMES = [
    'Wall',
    'Source',
    'EmptySpace',
]

CONE_MAT_NAMES = [
    'Wall',
    'Source',
    'EmptySpace',
]

ANAL_PARAMS = [
    'Name',
    'FWHM_122',
    'FWHM_662',
    'FWHM_1332',
    'kev_per_ch',
    'N_ch',
]

FILE_TYPE_TO_PREFIX = {
    'COAXIAL': 'DC_',
    'SCINTILLATOR': 'DS_',
    'COAX_WELL': 'DCW_',
    'POINT': '',
    'CYLINDER': 'SC_',
    'MARINELLI': 'SM_',
    'CONE': 'SK_',
}

FILE_TYPE_TO_MAT_NAME = {
    'COAXIAL': COAXIAL_MAT_NAMES,
    'SCINTILLATOR': SCINIL_MAT_NAMES,
    'COAX_WELL': COAX_WELL_MAT_NAMES,
    'POINT': [],
    'CYLINDER': CYL_MAT_NAMES,
    'MARINELLI': MAR_MAT_NAMES,
    'CONE': CONE_MAT_NAMES,
}