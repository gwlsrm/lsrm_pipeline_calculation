# common imports
from .operaton_interface import Operation  # noqa
from .operation_registry import register_operation  # noqa

# operations
from .appspec_convert_cr2spectrum_operation import AppspecConvertcr2spectrumOpertation  # noqa
from .appspec_convolute_straight_spec_operation import AppspecConvoluteStraightSpecOperation  # noqa
from .appspec_efficiency_input_prepare_operation import AppspecEfficiencyInputOperation  # noqa
from .appspec_efficiency_calculation_operation import AppspecEfficiencyOperation  # noqa
from .appspec_spectrum_input_prepare_operation import AppspecSpectrumInputOperation  # noqa
from .appspec_spectrum_calculation_operation import AppspecSpectrumOperation  # noqa
from .appspec_tsv_output_to_efr_operation import AppspecTsvOutputToEfr  # noqa
from .auto_efficiency_calibrate_operation import AutoEfficiencyCalibrationOperation  # noqa
from .copy_file_operation import CopyFileOperation  # noqa
from .detector_init_characterisation_operation import DetectorInitCharacterisationOperation  # noqa
# from .detector_precalc_grad_characterisation_operation import DetectorPrecalGradsCharacterisationOperation  # noqa
from .editinfile_operation import EditInFileOperation  # noqa
from .editjson_operation import EditJsonOperation  # noqa
from .effcalc_operation import EffCalcOperation  # noqa
from .effcalc_out_to_tsv_operation import EffCalcOutToTsvOperation  # noqa
from .efr_add_params_operation import EfrAddParametersOperation  # noqa
from .efr_from_efa_operation import EfrFromEfaOperation  # noqa
from .efr_to_tsv_operation import EfrToTsvOperation  # noqa
from .efr_update_from_tsv_operation import EfrUpdateFromTsvOperation  # noqa
from .for_files_operation import ForFilesOperation  # noqa
from .for_operation import ForOperation  # noqa
from .interpolate_efficiency_operation import LinearEfficiencyInterpolateOperation  # noqa
from .json_merge_files_operation import JsonMergeFilesOperation  # noqa
from .json_pretty_operation import JsonPrettyOperation  # noqa
from .json_to_tsv_operation import JsonToTsvOperation  # noqa
from .max_diff_between_2tsv_operation import CalcMaxDiffBetweenTwoColumns  # noqa
from .merge_input_files_operation import MergeFilesOperation  # noqa
from .merge_jsons_operation import MergeJsons  # noqa
from .physspec_operation import PhysspecOperation  # noqa
from .physspec_output_to_efr_operation import PhysspecOutputToEfrOperation  # noqa
from .physspec_print_distance import PhysspecPrintDistance  # noqa
from .physspec_set_rad_source import PhysspecSetRadSource  # noqa
from .plot_efficiency_operation import PlotEfficiencyOperation  # noqa
from .plot_tsv_2d_operation import PlotTsv2dOperation  # noqa
from .print_file_operation import PrintFileContent  # noqa
from .reduce_tsv_by_value_operation import ReduceTsvByValueOperation  # noqa
from .set_effmaker_distance_operation import SetEffMakerDistanceOperation  # noqa
from .spe2txt_converter_operation import Spe2TxtOperation  # noqa
from .sl_extended_object_efficiency_operation import ExtendedObjectEfficiencyOperation  # noqa
from .tsv_create_from_list_operation import TsvCreateFromList  # noqa
from .tsv_join_by_one_column_tccfcalc_operation import TsvOneColumnJoinOperation  # noqa
from .tsv_rename_columns_operation import TsvRenameColumnsOperation  # noqa
from .tsv_reduce_function_operations import TsvReduceFunctionOperation  # noqa
