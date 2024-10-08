# common imports
from .operaton_interface import Operation  # noqa
from .operation_registry import register_operation  # noqa

# operations
from .appspec_efficiency_input_prepare_operation import AppspecEfficiencyInputOperation  # noqa
from .appspec_operation import AppspecOperation  # noqa
from .appspec_tsv_output_to_efr_operation import AppspecTsvOutputToEfr  # noqa
try:
    from .auto_efficiency_calibrate_operation import AutoEfficiencyCalibrationOperation  # noqa
except ImportError as e:
    print("cannot import auto_efficiency_calibrate_operation:", e)
from .editinfile_operation import EditInFileOperation  # noqa
from .editjson_operation import EditJsonOperation  # noqa
from .effcalc_operation import EffCalcOperation  # noqa
from .efr_to_tsv_operation import EfrToTsvOperation  # noqa
from .for_operation import ForOperation  # noqa
from .interpolate_efficiency_operation import LinearEfficiencyInterpolateOperation  # noqa
from .json_pretty_operation import JsonPrettyOperation  # noqa
from .json_to_tsv_operation import JsonToTsvOperation  # noqa
from .max_diff_between_2tsv_operation import CalcMaxDiffBetweenTwoColumns  # noqa
from .merge_input_files_operation import MergeFilesOperation  # noqa
from .physspec_operation import PhysspecOperation  # noqa
from .plot_efficiency_operation import PlotEfficiencyOperation  # noqa
from .plot_tsv_2d_operation import PlotTsv2dOperation  # noqa
from .print_file_operation import PrintFileContent  # noqa
from .reduce_tsv_by_value_operation import ReduceTsvByValueOperation  # noqa
from .set_effmaker_distance_operation import SetEffMakerDistanceOperation  # noqa
