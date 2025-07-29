"""
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations
from typing import Self, Literal
import numpy as np
import numpy.typing as npt
import pandas as pd
from numbers import Number


def dprep(func):
    """this decorates a method that works on numpy arrays of shape equal to self.data.
    you can pass a nupy array or an instance of self.__class__. As long as the length
    is the same as self, 1, or len(self) == 1 it should construct the arguments for the decorated function.
    """

    def wrapper(self, b):
        bdat = self._dprep(b)

        if len(bdat) > 1 and len(self) == 1:
            a = self.tile(len(bdat))
        else:
            a = self
        return func(a, bdat)

    return wrapper


class Base:
    __array_priority__ = (
        15.0  # this is a quirk of numpy so the __r*__ methods here take priority
    )
    cols = []
    from_np_base = []
    from_np = []

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            if len(args) > 0:
                raise TypeError("Cannot accept args and kwargs at the same time")
            if all([c in kwargs for c in self.__class__.cols]):
                args = [kwargs[c] for c in self.__class__.cols]
            elif "data" in kwargs:
                args = [kwargs["data"]]
            else:
                raise TypeError(
                    f"unknown kwargs passed to {self.__class__.__name__}: {args}"
                )

        if len(args) == 1:
            if isinstance(args[0], np.ndarray) or isinstance(
                args[0], list
            ):  # data was passed directly
                self.data = self.__class__._clean_data(np.array(args[0]))

            elif all([isinstance(a, self.__class__) for a in args[0]]):
                # a list of self.__class__ is passed, concatenate into one
                self.data = self.__class__._clean_data(
                    np.concatenate([a.data for a in args[0]])
                )

            elif isinstance(args[0], pd.DataFrame):
                self.data = self.__class__._clean_data(np.array(args[0]))
            else:
                raise TypeError(
                    f"unknown args passed to {self.__class__.__name__}: {args[0]}"
                )

        elif len(args) == len(self.__class__.cols):
            # three args passed, each represents a col
            if all(isinstance(arg, Number) for arg in args):
                self.data = self.__class__._clean_data(np.array(args))
            elif all(isinstance(arg, np.ndarray) for arg in args):
                self.data = self.__class__._clean_data(np.array(args).T)
            elif all(isinstance(arg, list) for arg in args):
                self.data = self.__class__._clean_data(np.array(args).T)
            elif all(isinstance(arg, pd.Series) for arg in args):
                self.data = self.__class__._clean_data(
                    np.array(pd.concat(args, axis=1))
                )
            else:
                raise TypeError
        else:
            raise TypeError(f"Empty {self.__class__.__name__} not allowed")

    def to_numpy(self, cols: str | list = None):
        cols = self.cols if cols is None else cols
        return np.column_stack([getattr(self, c) for c in cols])

    @classmethod
    def from_numpy(Cls, data: npt.NDArray, cols: str | list):
        return Cls(np.column_stack([data[:, cols.index(col)] for col in Cls.cols]))

    @classmethod
    def _clean_data(cls, data) -> npt.NDArray[np.float64]:
        assert isinstance(data, np.ndarray)
        if data.dtype == "O":
            raise TypeError(
                f"data must have homogeneous shape for {cls.__name__}, given {data.shape}"
            )
        if len(data.shape) == 1:
            data = data.reshape(1, len(data))

        assert data.shape[1] == len(cls.cols)
        return data

    @classmethod
    def type_check(cls, a):
        return a if isinstance(a, cls) else cls(a)

    @classmethod
    def length_check(cls, a, b):
        if len(a) == 1 and len(b) > 1:
            a = a.tile(len(b))
        elif len(b) == 1 and len(a) > 1:
            b = b.tile(len(a))
        elif len(a) > 1 and len(b) > 1 and not len(a) == len(b):
            raise TypeError(
                f"lengths of passed arguments must be equal or 1, got {len(a)}, {len(b)}"
            )
        return a, b

    @classmethod
    def concatenate(cls, items) -> Self:
        return cls(np.concatenate([i.data for i in items], axis=0))

    def __getattr__(self, name) -> npt.NDArray[np.float64]:
        if name in self.__class__.cols:
            return self.data[:, self.__class__.cols.index(name)]
            # return res[0] if len(res) == 1 else res
        elif name in self.__class__.from_np + self.__class__.from_np_base:
            return self.__class__(getattr(np, name)(self.data))
        else:
            for col in self.__class__.cols:
                if len(name) > len(col):
                    if name[: len(col)] == col:
                        try:
                            id = int(name[len(col) :])
                        except ValueError:
                            break
                        return getattr(self, col)[id]

        raise AttributeError(f"Cannot get attribute {name}")

    def __dir__(self):
        return self.__class__.cols

    def __getitem__(self, sli) -> Self:
        return self.__class__(self.data[sli, :])

    def _dprep(self, other):
        l, w = len(self), len(self.cols)

        if isinstance(other, np.ndarray):
            if other.shape == (l, w):
                return other
            elif other.shape == (l, 1) or other.shape == (l,):
                return np.tile(other, (w, 1)).T
            elif other.shape == (1,):
                return np.full((l, w), other[0])
            elif l == 1:
                if len(other.shape) == 1:
                    return np.tile(other, (w, 1)).T
                elif other.shape[1] == w:
                    return other
                else:
                    raise ValueError(f"array shape {other.shape} not handled")
            else:
                raise ValueError(f"array shape {other.shape} not handled")
        elif isinstance(other, float) or isinstance(other, int):
            return np.full((l, w), other)
        elif isinstance(other, Base):
            a, b = self.__class__.length_check(self, other)
            return self._dprep(b.data)
        else:
            raise ValueError(f"unhandled datatype ({other.__class__.name})")

    def radians(self) -> Self:
        return self.__class__(np.radians(self.data))

    def degrees(self) -> Self:
        return self.__class__(np.degrees(self.data))

    def count(self) -> int:
        return len(self)

    def __len__(self) -> int:
        return self.data.shape[0]

    @property
    def ends(self) -> Self:
        return self.__class__(self.data[[0, -1], :])

    @dprep
    def __eq__(self, other):
        return np.all(self.data == other)

    @dprep
    def __add__(self, other) -> Self:
        return self.__class__(self.data + other)

    @dprep
    def __radd__(self, other) -> Self:
        return self.__class__(other + self.data)

    @dprep
    def __sub__(self, other) -> Self:
        return self.__class__(self.data - other)

    @dprep
    def __rsub__(self, other) -> Self:
        return self.__class__(other - self.data)

    @dprep
    def __mul__(self, other) -> Self:
        return self.__class__(self.data * other)

    @dprep
    def __rmul__(self, other) -> Self:
        return self.__class__(other * self.data)

    @dprep
    def __rtruediv__(self, other) -> Self:
        return self.__class__(other / self.data)

    @dprep
    def __truediv__(self, other) -> Self:
        return self.__class__(self.data / other)

    def __str__(self):
        means = " ".join(
            f"{c}_={v}" for c, v in zip(self.cols, np.mean(self.data, axis=0).round(2))
        )
        return f"{self.__class__.__name__}({means}, len={len(self)})"

    def __abs__(self):
        return np.linalg.norm(self.data, axis=1)

    def abs(self) -> Self:
        return self.__class__(np.abs(self.data))

    def __neg__(self) -> Self:
        return self.__class__(-self.data)

    def __pow__(self, power: Number) -> Self:
        return self.__class__(self.data ** power)

    @dprep
    def dot(self, other: Self) -> Self:
        return np.einsum("ij,ij->i", self.data, other)

    def diff(
        self, dt: npt.NDArray, method: Literal["gradient", "diff"] = "gradient"
    ) -> Self:
        if not pd.api.types.is_list_like(dt):
            dt = np.full(len(self), dt)
        self, dt = Base.length_check(self, dt)
        diff_method = np.gradient if method == "gradient" else np.diff

        data = diff_method(self.data, axis=0)
        dt = dt if method == "gradient" else dt[:-1]
        return self.__class__(data / np.tile(dt, (len(self.__class__.cols), 1)).T)

    def to_pandas(self, prefix="", suffix="", columns=None, index=None):
        if columns is not None:
            cols = columns
        else:
            cols = [prefix + col + suffix for col in self.__class__.cols]
        return pd.DataFrame(self.data, columns=cols, index=index)

    @property
    def df(self):
        return self.to_pandas()

    def tile(self, count) -> Self:
        return self.__class__(np.tile(self.data, (count, 1)))

    def to_dict(self):
        if len(self) == 1:
            return {key: getattr(self, key)[0] for key in self.cols}
        else:
            return {key: getattr(self, key) for key in self.cols}

    @classmethod
    def from_dict(Cls, data):
        return Cls(**data)

    def to_dicts(self):
        return self.to_pandas().to_dict("records")

    @classmethod
    def from_dicts(Cls, data: dict):
        return Cls(pd.DataFrame.from_dict(data))

    @classmethod
    def full(cls, val, count):
        return cls(np.tile(val.data, (count, 1)))

    def max(self):
        return self.__class__(self.data.max(axis=0))

    def min(self):
        return self.__class__(self.data.min(axis=0))

    def minloc(self):
        return self.__class__(self.data.argmin(axis=0))

    def maxloc(self):
        return self.__class__(self.data.argmax(axis=0))

    def cumsum(self):
        return self.__class__(np.cumsum(self.data, axis=0))

    def round(self, decimals=0):
        return self.__class__(self.data.round(decimals))

    def __repr__(self):
        return str(self)

    def copy(self):
        return self.__class__(self.data.copy())

    def unwrap(self, discont=np.pi):
        return self.__class__(np.unwrap(self.data, discont=discont, axis=0))

    def filter(self, order, cutoff, ts: np.ndarray = None):
        from scipy.signal import butter, freqz, filtfilt

        if ts is None:
            ts = np.array(range(len(self)))
        N = len(self)
        T = (ts[-1] - ts[0]) / N

        fs = 1 / T
        b, a = butter(order, cutoff, fs=fs, btype="low", analog=False)

        return self.__class__(filtfilt(b, a, self.data, axis=0))

    def fft(self, ts: np.ndarray = None):
        from scipy.fft import fft, fftfreq

        if ts is None:
            ts = np.array(range(len(self)))
        N = len(self) * 2
        T = (ts[-1] - ts[0]) / len(self)

        yf = fft(self.data, axis=0, n=N)
        xf = fftfreq(N, T)[: N // 2]

        y = 2.0 / N * np.abs(yf[0 : N // 2, :])

        return pd.DataFrame(
            np.column_stack([xf, y]), columns=["freq"] + self.cols
        ).set_index("freq")

    def fill_zeros(self):
        """fills zero length rows with the previous or next non-zero value"""
        return self.__class__(
            pd.DataFrame(
                np.where(
                    np.tile(abs(self) == 0, (3, 1)).T,
                    np.full(self.data.shape, np.nan),
                    self.data,
                )
            )
            .ffill()
            .bfill()
            .to_numpy()
        )

    def ffill(self):
        return self.__class__(pd.DataFrame(self.data).ffill().to_numpy())

    def bfill(self):
        return self.__class__(pd.DataFrame(self.data).bfill().to_numpy())

    def linterp(
        self,
        index: npt.NDArray | pd.Index,
        extrapolate: Literal["throw", "nearest"] = "throw",
    ):
        "linear interpolation"
        index = pd.Index(np.arange(len(self)) if index is None else index)
        assert len(index) == len(self)
        assert pd.Index(index).is_monotonic_increasing

        def dolinterp(ts: npt.NDArray | Number):
            starts = index.get_indexer(ts, method="ffill")
            stops = index.get_indexer(ts, method="bfill")
            if np.any(starts * stops < 0) and extrapolate=="throw":
                raise Exception("Cannot extrapolate beyond parent range")
            return self.__class__(np.column_stack(
                [
                    np.interp(
                        ts, index, self.data[:, i], self.data[0, i], self.data[-1, i]
                    )
                    for i, col in enumerate(self.cols)
                ]
            ))
            # return lambda t: a + (b - a) * np.clip(t, 0, 1)
        return dolinterp
    
    def bspline(self, index: npt.NDArray | pd.Index = None):
        from scipy.interpolate import make_interp_spline

        bspline = make_interp_spline(
            np.arange(len(self)) if index is None else index, self.data, axis=0
        )
        return lambda i: self.__class__(bspline(i))

    def interpolate(self, index: npt.NDArray | pd.Index = None, method:str=None):
        if method is None:
            match (self.__class__.__name__):
                case "Point":
                    method="bspline"
                case "Quaternion":
                    method="slerp"
                case "Time":
                    method="linterp"
        return getattr(self, method)(index)

    def plot(self, index=None, **kwargs):
        import plotly.graph_objects as go

        fig = go.Figure()
        for col in self.cols:
            fig.add_trace(
                go.Scatter(
                    x=np.arange(len(self)) if index is None else index,
                    y=getattr(self, col),
                    name=col,
                    **kwargs,
                )
            )
        # df = self.to_pandas(self.__class__.__name__[0], index=index)
        return fig
