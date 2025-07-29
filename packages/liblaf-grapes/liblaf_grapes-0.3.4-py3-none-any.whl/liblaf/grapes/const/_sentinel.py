import enum


class Sentinel(enum.Enum):
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({self.name!r})"


class MissingType(Sentinel):
    MISSING = enum.auto()


MISSING = MissingType.MISSING


class NopType(Sentinel):
    NOP = enum.auto()


NOP = NopType.NOP
