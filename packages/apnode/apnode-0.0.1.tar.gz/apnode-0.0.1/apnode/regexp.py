import re

from .value import create_value


class Regexp:
    def __init__(self, rule: str, field=None):
        self.rule = rule
        self.field = field
        self.exp = re.compile(str(rule))

    def __repr__(self):
        return self.rule

    def find_map(self, content):
        content = str(content)
        match = self.exp.match(content)
        if match is None:
            return None
        dic = {}
        groups = match.groupdict()
        for k in groups:
            if groups[k] is not None:
                dic[k] = create_value(groups[k])
        return dic

    def is_match(self, content):
        match = self.exp.findall(str(content))
        return len(match) > 0

    def is_match2(self, content):
        match = self.exp.match(str(content))
        return match is not None


if __name__ == '__main__':
    exp = Regexp("^^(?P<word>[a-zA-Z]+)(.*)|$")
    find = exp.find_map("swda?")
    print(find)
