from __future__ import annotations
import ctypes
import typing

T = typing.TypeVar("T")
c_lib = None

def init_lib(path):
    """Initializes the native library. Must be called at least once before anything else."""
    global c_lib
    c_lib = ctypes.cdll.LoadLibrary(path)

    c_lib.calculate_performance_from_path.argtypes = [ctypes.POINTER(ctypes.c_int8), ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, Optionf64, Optionu32, Optionu32, Optionu32, ctypes.c_uint32, Optionu32]
    c_lib.calculate_performance_from_bytes.argtypes = [Sliceu8, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, Optionf64, Optionu32, Optionu32, Optionu32, ctypes.c_uint32, Optionu32]

    c_lib.calculate_performance_from_path.restype = CalculatePerformanceResult
    c_lib.calculate_performance_from_bytes.restype = CalculatePerformanceResult



def calculate_performance_from_path(beatmap_path: ctypes.POINTER(ctypes.c_int8), mode: int, mods: int, max_combo: int, accuracy: Optionf64, count_300: Optionu32, count_100: Optionu32, count_50: Optionu32, miss_count: int, passed_objects: Optionu32) -> CalculatePerformanceResult:
    return c_lib.calculate_performance_from_path(beatmap_path, mode, mods, max_combo, accuracy, count_300, count_100, count_50, miss_count, passed_objects)

def calculate_performance_from_bytes(beatmap_bytes: Sliceu8 | ctypes.Array[ctypes.c_uint8], mode: int, mods: int, max_combo: int, accuracy: Optionf64, count_300: Optionu32, count_100: Optionu32, count_50: Optionu32, miss_count: int, passed_objects: Optionu32) -> CalculatePerformanceResult:
    if hasattr(beatmap_bytes, "_length_") and getattr(beatmap_bytes, "_type_", "") == ctypes.c_uint8:
        beatmap_bytes = Sliceu8(data=ctypes.cast(beatmap_bytes, ctypes.POINTER(ctypes.c_uint8)), len=len(beatmap_bytes))

    return c_lib.calculate_performance_from_bytes(beatmap_bytes, mode, mods, max_combo, accuracy, count_300, count_100, count_50, miss_count, passed_objects)





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


class CalculatePerformanceResult(ctypes.Structure):

    # These fields represent the underlying C data layout
    _fields_ = [
        ("pp", ctypes.c_double),
        ("stars", ctypes.c_double),
        ("ar", ctypes.c_double),
        ("od", ctypes.c_double),
        ("max_combo", ctypes.c_uint32),
    ]

    def __init__(self, pp: float = None, stars: float = None, ar: float = None, od: float = None, max_combo: int = None):
        if pp is not None:
            self.pp = pp
        if stars is not None:
            self.stars = stars
        if ar is not None:
            self.ar = ar
        if od is not None:
            self.od = od
        if max_combo is not None:
            self.max_combo = max_combo

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

    @property
    def ar(self) -> float:
        return ctypes.Structure.__get__(self, "ar")

    @ar.setter
    def ar(self, value: float):
        return ctypes.Structure.__set__(self, "ar", value)

    @property
    def od(self) -> float:
        return ctypes.Structure.__get__(self, "od")

    @od.setter
    def od(self, value: float):
        return ctypes.Structure.__set__(self, "od", value)

    @property
    def max_combo(self) -> int:
        return ctypes.Structure.__get__(self, "max_combo")

    @max_combo.setter
    def max_combo(self, value: int):
        return ctypes.Structure.__set__(self, "max_combo", value)


class Optionf64(ctypes.Structure):
    """May optionally hold a value."""

    _fields_ = [
        ("_t", ctypes.c_double),
        ("_is_some", ctypes.c_uint8),
    ]

    @property
    def value(self) -> ctypes.c_double:
        """Returns the value if it exists, or None."""
        if self._is_some == 1:
            return self._t
        else:
            return None

    def is_some(self) -> bool:
        """Returns true if the value exists."""
        return self._is_some == 1

    def is_none(self) -> bool:
        """Returns true if the value does not exist."""
        return self._is_some != 0


class Optionu32(ctypes.Structure):
    """May optionally hold a value."""

    _fields_ = [
        ("_t", ctypes.c_uint32),
        ("_is_some", ctypes.c_uint8),
    ]

    @property
    def value(self) -> ctypes.c_uint32:
        """Returns the value if it exists, or None."""
        if self._is_some == 1:
            return self._t
        else:
            return None

    def is_some(self) -> bool:
        """Returns true if the value exists."""
        return self._is_some == 1

    def is_none(self) -> bool:
        """Returns true if the value does not exist."""
        return self._is_some != 0


class Sliceu8(ctypes.Structure):
    # These fields represent the underlying C data layout
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("len", ctypes.c_uint64),
    ]

    def __len__(self):
        return self.len

    def __getitem__(self, i) -> int:
        if i < 0:
            index = self.len+i
        else:
            index = i

        if index >= self.len:
            raise IndexError("Index out of range")

        return self.data[index]

    def copied(self) -> Sliceu8:
        """Returns a shallow, owned copy of the underlying slice.

        The returned object owns the immediate data, but not the targets of any contained
        pointers. In other words, if your struct contains any pointers the returned object
        may only be used as long as these pointers are valid. If the struct did not contain
        any pointers the returned object is valid indefinitely."""
        array = (ctypes.c_uint8 * len(self))()
        ctypes.memmove(array, self.data, len(self) * ctypes.sizeof(ctypes.c_uint8))
        rval = Sliceu8(data=ctypes.cast(array, ctypes.POINTER(ctypes.c_uint8)), len=len(self))
        rval.owned = array  # Store array in returned slice to prevent memory deallocation
        return rval

    def __iter__(self) -> typing.Iterable[ctypes.c_uint8]:
        return _Iter(self)

    def iter(self) -> typing.Iterable[ctypes.c_uint8]:
        """Convenience method returning a value iterator."""
        return iter(self)

    def first(self) -> int:
        """Returns the first element of this slice."""
        return self[0]

    def last(self) -> int:
        """Returns the last element of this slice."""
        return self[len(self)-1]

    def bytearray(self):
        """Returns a bytearray with the content of this slice."""
        rval = bytearray(len(self))
        for i in range(len(self)):
            rval[i] = self[i]
        return rval




class callbacks:
    """Helpers to define callbacks."""


