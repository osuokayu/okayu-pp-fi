from __future__ import annotations
import ctypes
import typing

T = typing.TypeVar("T")
c_lib = None

def init_lib(path):
    """Initializes the native library. Must be called at least once before anything else."""
    global c_lib
    c_lib = ctypes.cdll.LoadLibrary(path)

    c_lib.calculate_score.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_double, ctypes.c_uint32]

    c_lib.calculate_score.restype = CalculateResult



def calculate_score(beatmap_path: str, mode: int, mods: int, max_combo: int, accuracy: float, miss_count: int) -> CalculateResult:
    if not hasattr(beatmap_path, "__ctypes_from_outparam__"):
        beatmap_path = ctypes.cast(beatmap_path, ctypes.POINTER(ctypes.c_char))
    return c_lib.calculate_score(beatmap_path, mode, mods, max_combo, accuracy, miss_count)





TRUE = ctypes.c_uint8(1)
FALSE = ctypes.c_uint8(0)


def _errcheck(returned, success):
    """Checks for FFIErrors and converts them to an exception."""
    if returned == success: return
    else: raise Exception(f"Function returned error: {returned}")


class CallbackVars(object):
    """Helper to be used `lambda x: setattr(cv, "x", x)` when getting values from callbacks."""
    def __str__(self):
        rval = ""
        for var in  filter(lambda x: "__" not in x, dir(self)):
            rval += f"{var}: {getattr(self, var)}"
        return rval


class _Iter(object):
    """Helper for slice iterators."""
    def __init__(self, target):
        self.i = 0
        self.target = target

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i >= self.target.len:
            raise StopIteration()
        rval = self.target[self.i]
        self.i += 1
        return rval


class CalculateResult(ctypes.Structure):

    # These fields represent the underlying C data layout
    _fields_ = [
        ("pp", ctypes.c_double),
        ("stars", ctypes.c_double),
    ]

    def __init__(self, pp: float = None, stars: float = None):
        if pp is not None:
            self.pp = pp
        if stars is not None:
            self.stars = stars

    @property
    def pp(self) -> float:
        return ctypes.Structure.__get__(self, "pp")

    @pp.setter
    def pp(self, value: float):
        return ctypes.Structure.__set__(self, "pp", value)

    @property
    def stars(self) -> float:
        return ctypes.Structure.__get__(self, "stars")

    @stars.setter
    def stars(self, value: float):
        return ctypes.Structure.__set__(self, "stars", value)




class callbacks:
    """Helpers to define callbacks."""


