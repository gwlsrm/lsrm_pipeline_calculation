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


def _transpose(lst: tp.List[tp.List[tp.Any]]) -> tp.List[tp.List[tp.Any]]:
    return list(zip(*lst))


def _make_iterable(var_params_rec: tp.List[tp.Dict[str, tp.Any]]):
    names = []
    values = []
    for param_rec in var_params_rec:
        names.append(param_rec['name'])
        values.append(param_rec['values'])
    return names, _transpose(values)


@register_operation
class ForOperation:
    """
    ForOperation -- special operation: creates N branches for graph in params
    parameters:
        - var_params: list of parameters for ForOperation: [name: param_name, values: [v1, v2, ...]]
        - operations: list of operations, they can contain $param_name,
            new param value will be set for each for iteration
    """
    def __init__(self):
        self.operations: tp.List[Operation] = []

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'ForOperation':
        op = ForOperation()
        assert len(section['var_params']) > 0
        names, var_params = _make_iterable(section['var_params'])
        for params in var_params:
            assert len(names) == len(params)
            for operation_rec in section['operations']:
                operation_rec = _update_operation_rec(operation_rec, names, params)
                t = register_operation.registry[operation_rec['type']]
                operation = t.parse_from_yaml(operation_rec, project_dir)
                op.operations.append(operation)
        return op

    def run(self) -> None:
        print('start for')
        for op in self.operations:
            op.run()
