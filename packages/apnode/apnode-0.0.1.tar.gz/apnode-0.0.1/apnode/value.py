


class Value:
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Value):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self):
        return self.value.__hash__()

    def strip(self):
        return Value(self.value.strip())

    def to_reg(self):
        from .regexp import Regexp
        return Regexp(self.value)

    def to_int(self) -> int:
        try:
            return int(self.value)
        except Exception:
            print("无法将[", self.value, "]转换为int")
        return 0

    def to_float(self) -> float:
        try:
            return float(self.value)
        except Exception:
            print("无法将[", self.value, "]转换为float")
        return 0.

    def to_float_with_err(self) -> float:
        return float(self.value)

    def to_str(self):
        return self.value

    def split_by_space(self):
        splits = self.value.strip().split(" ")
        s = [s for s in splits if s != ""]
        return s


def create_value(value):
    if isinstance(value, str):
        return Value(value)
    elif isinstance(value, Value):
        return value
    else:
        print("创建Value错误, 不支持类型: {}".format(type(value)))
