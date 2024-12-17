import glob
import os
import typing as tp

from operations.operation_registry import register_operation
from .operaton_interface import Operation


def _update_str(section: str, names: tp.List[str], params: tp.List[tp.Any]) -> str:
    for name, value in zip(names, params):
        template = '${' + name + '}'
        if section == template:
            return value
        if template in section:
            section = section.replace(template, str(value))
    return section


def _update_operation_rec(section: tp.Any, names: tp.List[str], params: tp.List[tp.Any]) -> tp.Any:
    if isinstance(section, dict):
        return {k: _update_operation_rec(v, names, params) for k, v in section.items()}
    elif isinstance(section, list):
        return [_update_operation_rec(r, names, params) for r in section]
    elif type(section) is str:
        return _update_str(section, names, params)
    else:
        return section


def _update_operation(section, filepath: str):
    filedir, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    return _update_operation_rec(section, names=["FILEPATH", "FILEDIR", "FILENAME", "NAME", "EXT"],
                                 params=[filepath, filedir, filename, name, ext])


@register_operation
class ForFilesOperation:
    """
    ForFilesOperation -- start operation for every file in folder
    parameters:
        input_filemask: filemask to run for, e.g. path/*.txt
        operations: list of operations, they can contain:
          ${FILENAME}, ${FILEPATH}, ${FILEDIR}, ${NAME}, ${EXT}
    """
    def __init__(self):
        self.input_filemask = ""
        self.operation_params: tp.List[tp.Dict[str, tp.Any]] = []
        self.project_dir = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'ForFilesOperation':
        op = ForFilesOperation()
        op.input_filemask = os.path.join(project_dir, section["input_filemask"])
        op.operation_params = section['operations']
        op.project_dir = project_dir
        return op

    def run(self) -> None:
        print('start for_files operation')
        for filepath in glob.glob(self.input_filemask):
            if not os.path.isfile(filepath):
                continue
            for operation_rec in self.operation_params:
                operation_rec = _update_operation(operation_rec, filepath)
                t = register_operation.registry[operation_rec['type']]
                operation = t.parse_from_yaml(operation_rec, self.project_dir)
                operation.run()
