import json
import os
import typing as tp

import numpy as np

from operations.operation_registry import register_operation


def _check_source(source: tp.Dict[str, tp.Any]) -> None:
    expected_keys = ["from", "to", "points", "intensity", "is_log"]
    for k in expected_keys:
        assert k in source.keys(), f"{k} is not in source"


def _generate_rad_source(source: tp.Dict[str, tp.Any]) -> tp.List[tp.Dict[str, tp.Any]]:
    if source["is_log"]:
        grid = np.geomspace(source["from"], source["to"], source["points"])
    else:
        grid = np.linspace(source["from"], source["to"], source["points"])
    return [{"E": e, "I": source["intensity"]} for e in grid]


def _sets_rad_source(input_filename: str, cell_number: int, source: tp.Dict[str, tp.Any],
                     output_filename: str, is_pretty: bool):
    with open(input_filename) as f:
        config = json.load(f)

    config["ContainerSource"]["Cells"][cell_number]["RadioactiveSource"] = _generate_rad_source(source)

    indent = 4 if is_pretty else None
    with open(output_filename, 'w') as f:
        json.dump(config, f, indent=indent)


@register_operation
class PhysspecSetRadSource:
    """
    PhysspecSetRadSource sets radioactive source section to container cell in physspec_input.json
    parameters:
        input_filename: physspec_input.json
        output_filename: physspec_input.json
        cell_number: number of cell where to set rad. source
        source: dict with keys: from, to, points, intensity, is_log
        is_pretty: make output json pretty
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""
        self.cell_number = 0
        self.source = None
        self.is_pretty = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> (
            'PhysspecSetRadSource'):
        op = PhysspecSetRadSource()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.cell_number = section["cell_number"]
        op.source = section['source']
        op.is_pretty = section.get("is_pretty", op.is_pretty)
        _check_source(op.source)
        return op

    def run(self) -> None:
        print('start physspec_set_rad_source')
        _sets_rad_source(self.input_filename, self.cell_number, self.source, self.output_filename,
                         self.is_pretty)
