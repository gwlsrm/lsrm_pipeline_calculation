import os.path
import struct
import sys
import typing as tp


def get_output_filename(input_filename: str) -> str:
    filename, _ = os.path.splitext(input_filename)
    return filename + '.txt'


def read_double_bin_array(filename: str) -> tp.List[float]:
    """
    read double array from binary file.
    format: array_size: int_32, array: double*
    """
    with open(filename, 'rb') as f:
        arr_size_struct = f.read(4)
        arr_size = struct.unpack('i', arr_size_struct)[0]
        arr = []
        for _ in range(arr_size):
            s = f.read(8)
            d = struct.unpack('d', s)[0]
            arr.append(d)
    return arr


def convert_from_bin_to_txt(input_filename: str, output_filename: str) -> None:
    """convert binary-file with array of double to txt file"""
    arr = read_double_bin_array(input_filename)

    with open(output_filename, 'w') as f:
        for n in arr:
            f.write(str(n))
            f.write('\n')


def main():
    if len(sys.argv) <= 1:
        sys.exit()

    input_filename = sys.argv[1]
    output_filename = get_output_filename(input_filename)

    convert_from_bin_to_txt(input_filename, output_filename)


if __name__ == "__main__":
    main()
