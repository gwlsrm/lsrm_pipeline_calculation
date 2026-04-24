"""
    Parser for config files like *.ini, but without sections
"""
class ConfigFileParser:
    def __init__(self, filename, sep='='):
        self.data = {}
        self.filename = filename
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if ConfigFileParser.is_comment(line): continue
                words = [word.strip() for word in line.split('=')]
                if len(words) < 2: continue
                self.data[words[0]] = '='.join(words[1:])

    def get_dict(self):
        return self.data

    def get(self, key, cast_type=None, default=None):
        value = self.data.get(key, default)
        if cast_type is not None:
            try:
                value = cast_type(value)
            except:
                return default
        return value

    def __contains__(self, key):
        return key in self.data

    @staticmethod
    def is_comment(line):
        return line.startswith('#') or line.startswith('//')