import json
import os
import typing as tp

from operations.operation_registry import register_operation


@register_operation
class JsonPrettyOperation:
    """
    JsonPrettyOperation pretifies json-file: adds indent (=4)
    """
    def __init__(self):
        self.input_filename = ""
        self.output_filename = ""

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'JsonPrettyOperation':
        op = JsonPrettyOperation()
        op.input_filename = os.path.join(project_dir, section['input_filename'])
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        return op

    def run(self) -> None:
        print('start json pretty')
        with open(self.input_filename) as f:
            data = json.load(f)
        with open(self.output_filename, 'w') as g:
            json.dump(data, g, indent=4)
