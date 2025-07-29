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
from typing import Literal
from .base import Base
import numpy as np
import pandas as pd
from warnings import warn
from numbers import Number
import numpy.typing as npt


class Point(Base):
    cols = ["x", "y", "z"]
    from_np = [
        "sin",
        "cos",
        "tan",
        "arcsin",
        "arccos",
        "arctan",
    ]

    @property
    def xy(self):
        return Point(self.x, self.y, np.zeros(len(self)))

    @property
    def yz(self):
        return Point(np.zeros(len(self)), self.y, self.z)

    @property
    def zx(self):
        return Point(self.x, np.zeros(len(self)), self.z)

    def scale(self, value) -> Point:
        with np.errstate(divide="ignore"):
            res = value / abs(self)
        res[res == np.inf] = 0
        return self * res

    def unit(self) -> Point:
        return self.scale(1)

    def remove_outliers(self, nstds=2):
        ab = abs(self)
        std = np.nanstd(ab)
        mean = np.nanmean(ab)

        data = self.data.copy()

        data[abs(ab - mean) > nstds * std, :] = [np.nan, np.nan, np.nan]

        return Point(pd.DataFrame(data).ffill().bfill().to_numpy())

    def mean(self):
        return Point(np.mean(self.data, axis=0))

    def max(self):
        return Point(np.max(self.data, axis=0))

    def min(self):
        return Point(np.min(self.data, axis=0))

    def angles(self, p2):
        return (self.cross(p2) / (abs(self) * abs(p2))).arcsin

    def planar_angles(self):
        return Point(
            np.arctan2(self.y, self.z),
            np.arctan2(self.z, self.x),
            np.arctan2(self.x, self.y),
        )

    def angle(self, p2):
        return abs(Point.angles(self, p2))

    @staticmethod
    def X(value: Number | npt.NDArray = 1, count=1):
        return np.tile(value, count) * Point(1, 0, 0)

    @staticmethod
    def Y(value=1, count=1):
        return np.tile(value, count) * Point(0, 1, 0)

    @staticmethod
    def Z(value=1, count=1):
        return np.tile(value, count) * Point(0, 0, 1)

    def rotate(self, rmat=np.ndarray):
        if len(rmat.shape) == 3:
            pass
        elif len(rmat.shape) == 2:
            rmat = np.reshape(rmat, (1, 3, 3))
        else:
            raise TypeError("expected a 3x3 matrix")

        return self.dot(rmat)

    def to_rotation_matrix(self):
        """returns the rotation matrix based on a point representing Euler angles"""
        s = self.sin
        c = self.cos
        return np.transpose(
            np.array(
                [
                    [
                        c.z * c.y,
                        c.z * s.y * s.x - c.x * s.z,
                        c.x * c.z * s.y + s.x * s.z,
                    ],
                    [
                        c.y * s.z,
                        c.x * c.z + s.x * s.y * s.z,
                        -1 * c.z * s.x + c.x * s.y * s.z,
                    ],
                    [-1 * s.y, c.y * s.x, c.x * c.y],
                ]
            ),
            (2, 0, 1),
        )

    def matrix(self):
        return np.einsum("i...,...->i...", self.data, np.identity(3))

    @staticmethod
    def from_matrix(matrix):
        return Point(matrix[:, 0, 0], matrix[:, 1, 1], matrix[:, 2, 2])

    def skew_symmetric(self):
        o = np.zeros(len(self))
        return np.transpose(
            np.array(
                [[o, -self.z, self.y], [self.z, o, -self.x], [-self.y, self.x, o]]
            ),
            (2, 0, 1),
        )

    @staticmethod
    def zeros(count=1):
        return Point(np.zeros((count, 3)))

    @staticmethod
    def circle_xy(radius: float, n: int) -> Point:
        """
        Generate points on a circle in the specified plane.
        
        :param radius: Radius of the circle.
        :param n: Number of points to generate.
        :return: Points on the circle as a Point object.
        """
        
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return Point(radius * np.cos(angles), radius * np.sin(angles), np.zeros(n))

    @staticmethod
    def ellipse_xy(a: float, b: float, n: int) -> Point:
        """
        Generate points on an ellipse in the specified plane.
        
        :param a: Semi-major axis length.
        :param b: Semi-minor axis length.
        :param n: Number of points to generate.
        :return: Points on the ellipse as a Point object.
        """
        
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return Point(a * np.cos(angles), b * np.sin(angles), np.zeros(n))

    def bearing(self):
        return np.arctan2(self.y, self.x)

    def plot3d(self, fig=None, **kwargs):
        import plotly.graph_objects as go

        _fig = go.Figure() if fig is None else fig

        _fig.add_trace(go.Scatter3d(x=self.x, y=self.y, z=self.z, **kwargs))
        if fig is None:
            _fig.update_layout(scene=dict(aspectmode="data"))
        return _fig

    def plotxy(self):
        import plotly.express as px

        return px.line(self.df, x="x", y="y").update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )

    def plotyz(self):
        import plotly.express as px

        return px.line(self.df, x="y", y="z").update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1, title="z"), xaxis=dict(title="y")
        )

    def plotzx(self):
        import plotly.express as px

        return px.line(self.df, x="z", y="x").update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1, title="x"), xaxis=dict(title="z")
        )
    def plotxz(self):
        import plotly.express as px

        return px.line(self.df, x="x", y="z").update_layout(
            yaxis=dict(scaleanchor="x", scaleratio=1, title="x"), xaxis=dict(title="z")
        )
    def arbitrary_perpendicular(self) -> Point:
        min_axes = np.argmin(np.abs(self.data), axis=1)
        cvecs = Point.concatenate(
            [Point(*[1 if axis == i else 0 for i in np.arange(3)]) for axis in min_axes]
        )
        return cross(self, cvecs)


def Points(*args, **kwargs):
    warn("Points is deprecated, you can now just use Point", DeprecationWarning)
    return Point(*args, **kwargs)


def PX(length=1, count=1):
    return Point.X(length, count)


def PY(length=1, count=1):
    return Point.Y(length, count)


def PZ(length=1, count=1):
    return Point.Z(length, count)


def P0(count=1):
    return Point.zeros(count)


def ppmeth(func):
    def wrapper(a, b, *args, **kwargs):
        assert all([isinstance(arg, Point) for arg in args])
        assert len(a) == len(b) or len(a) == 1 or len(b) == 1
        return func(a, b, *args, **kwargs)

    setattr(Point, func.__name__, wrapper)
    return wrapper


@ppmeth
def cross(a: Point, b: Point) -> Point:
    return Point(np.cross(a.data, b.data))


@ppmeth
def cos_angle_between(a: Point, b: Point) -> np.ndarray:
    return a.unit().dot(b.unit())


@ppmeth
def angle_between(a: Point, b: Point) -> np.ndarray:
    return np.arccos(a.cos_angle_between(b))


@ppmeth
def scalar_projection(a: Point, b: Point) -> Point:
    return a.cos_angle_between(b) * abs(a)


@ppmeth
def vector_projection(a: Point, b: Point) -> Point:
    return b.scale(a.scalar_projection(b))


@ppmeth
def vector_rejection(a: Point, b: Point) -> Point:
    return a - ((Point.dot(a, b)) / Point.dot(b, b)) * b


@ppmeth
def is_parallel(a: Point, b: Point, tolerance=1e-6):
    return abs(a.cos_angle_between(b) - 1) < tolerance


@ppmeth
def is_perpendicular(a: Point, b: Point, tolerance=1e-6):
    return abs(a.dot(b)) < tolerance


@ppmeth
def min_angle_between(p1: Point, p2: Point):
    angle = angle_between(p1, p2) % np.pi
    return np.minimum(angle, np.pi - angle)


def vector_norm(point: Point):
    return abs(point)


def normalize_vector(point: Point):
    return point / abs(point)
