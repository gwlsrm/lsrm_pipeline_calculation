import typing as tp


def parse_out_file_col_format(filename: str) -> tp.Dict[str, tp.List[float]]:
    """
    parse_out_file_col_format -- parses tccfcalc.out files,
        returns dict: col_name -> column
    """
    with open(filename) as f:
        lines = [line.rstrip() for line  in f]

    # search header
    header_line_num = None
    for i, line in enumerate(lines):
        if line == "Results:":
            header_line_num = i
            break
    if header_line_num is None:
        raise RuntimeError('Cannot find data (tag "Results:")')
    header_line_num += 2

    # read header
    header = lines[header_line_num].split('\t')

    # read data
    data_i = header_line_num + 2
    data = {}
    for i in range(data_i, len(lines)):
        if lines[i].startswith('--'):
            break
        d = [float(t) for t in lines[i].split('\t')]
        for n, v in zip(header, d):
            data.setdefault(n, [])
            data[n].append(v)
    return data


def parse_out_file_row_format(filename: str) -> tp.Tuple[tp.List[str], tp.List[tp.List[float]]]:
    """
    parse_out_file_row_format -- parses tccfcalc.out files,
        returns table header and data as list of rows
    """
    with open(filename) as f:
        lines = [line.rstrip() for line  in f]

    # search header
    header_line_num = None
    for i, line in enumerate(lines):
        if line == "Results:":
            header_line_num = i
            break
    if header_line_num is None:
        raise RuntimeError('Cannot find data (tag "Results:")')
    header_line_num += 2

    # read header
    header = lines[header_line_num].split('\t')

    # read data
    data_i = header_line_num + 2
    data = []
    for i in range(data_i, len(lines)):
        if lines[i].startswith('--'):
            break
        d = [float(t) for t in lines[i].split('\t')]
        data.append(d)
    return header, data
