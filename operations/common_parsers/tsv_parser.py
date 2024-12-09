import typing as tp


def _get_type(v: str) -> tp.Any:
    if v.lower() in ("true", "false"):
        return bool
    try:
        int(v)
        return int
    except ValueError:
        pass
    try:
        float(v)
        return float
    except ValueError:
        pass
    return str


def parse_tsv_to_str_cols(filename: str) -> tp.Dict[str, tp.List[str]]:
    header_names = None
    res: tp.Dict[str, tp.List[str]] = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if header_names is None:
                header_names = [w for w in line.split('\t')]
                continue
            tokens = [w for w in line.split('\t')]
            assert len(tokens) == len(header_names)
            for name, value in zip(header_names, tokens):
                res.setdefault(name, [])
                res[name].append(value)
    return res


def parse_tsv_to_float_cols(filename: str) -> tp.Dict[str, tp.List[float]]:
    header_names = None
    res: tp.Dict[str, tp.List[str]] = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if header_names is None:
                header_names = [w for w in line.split('\t')]
                continue
            tokens = [float(w) for w in line.split('\t')]
            assert len(tokens) == len(header_names)
            for name, value in zip(header_names, tokens):
                res.setdefault(name, [])
                res[name].append(value)
    return res


def parse_tsv_to_cols(filename: str) -> tp.Dict[str, tp.List[tp.Any]]:
    header_names = None
    res: tp.Dict[str, tp.List[str]] = {}
    types = None
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if header_names is None:
                header_names = [w for w in line.split('\t')]
                continue
            if types is None:
                types = [_get_type(w) for w in line.split('\t')]
            tokens = [types[i](w) for i, w in enumerate(line.split('\t'))]
            assert len(tokens) == len(header_names)
            for name, value in zip(header_names, tokens):
                res.setdefault(name, [])
                res[name].append(value)
    return res


def parse_tsv_to_str_rows(filename: str) -> tp.Tuple[tp.List[str], tp.List[tp.List[str]]]:
    header = None
    res: tp.List[tp.List[str]] = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if header is None:
                header = list(line.split('\t'))
                continue
            row = [w for w in line.split('\t')]
            assert len(row) == len(header)
            res.append(row)
    return header, res


def save_rows_to_tsv(output_filename: str, header: tp.List[str], rows: tp.List[tp.List[str]]):
    with open(output_filename, 'w') as f:
        f.write("\t".join(header))
        f.write("\n")
        for row in rows:
            f.write("\t".join(row))
            f.write("\n")
