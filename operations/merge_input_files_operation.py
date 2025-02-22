import os
import typing as tp

from operations.operation_registry import register_operation


def _merge_files(input_filenames: tp.List[str], output_filename: str, write_filename: bool,
                 write_header: bool, write_eol_between_files: bool):
    with open(output_filename, 'w') as g:
        if write_header:
            g.write("filename\tfilecontent\n")
        for input_filename in input_filenames:
            if write_filename:
                g.write(f"{input_filename}\t")
            with open(input_filename) as f:
                for line in f:
                    g.write(line)
                if write_eol_between_files:
                    g.write('\n')


@register_operation
class MergeFilesOperation:
    """
    MergeFilesOperation merge all text files to one
    parameters:
        input_filenames: list of text filenames to merge
        output_filename: desirable output filename
        write_filename: will add filename: filename\tfilecontent
        write_header: will write header: "filename\tfilecontent\n",
            it's useful if inputfiles have only one line
        write_eol_between_files: will write \n between file contents
    """
    def __init__(self):
        self.input_filenames: tp.List[str] = []
        self.output_filename: str = ""
        self.write_filename: bool = False
        self.write_header: bool = False
        self.write_eol_between_files: bool = False

    @staticmethod
    def parse_from_yaml(section: tp.Dict[str, tp.Any], project_dir: str) -> 'MergeFilesOperation':
        op = MergeFilesOperation()
        op.input_filenames = [
            os.path.join(project_dir, input_filename)
            for input_filename in section['input_filenames']]
        op.output_filename = os.path.join(project_dir, section['output_filename'])
        op.write_filename = section.get("write_filename", False)
        op.write_header = section.get("write_header", False)
        op.write_eol_between_files = section.get("write_eol_between_files", False)
        return op

    def run(self) -> None:
        print('start merge files')
        _merge_files(self.input_filenames, self.output_filename, self.write_filename,
                     self.write_header, self.write_eol_between_files)
