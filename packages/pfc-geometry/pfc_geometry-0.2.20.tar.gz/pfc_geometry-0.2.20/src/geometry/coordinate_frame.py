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
from geometry import Point, Quaternion, PX, PY, PZ, P0
from typing import List
import numpy as np
import pandas as pd
from geometry.base import Base


class Coord(Base):
    cols = [
        "ox", "oy", "oz",
        "x1", "y1", "z1",
        "x2", "y2", "z2",
        "x3", "y3", "z3",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin=Point(self.data[:,:3])
        self.x_axis=Point(self.data[:,3:6])
        self.y_axis=Point(self.data[:,6:9])
        self.z_axis=Point(self.data[:,9:12])
    
    @staticmethod
    def from_axes(o:Point, x:Point, y:Point, z:Point) -> Coord:
        assert len(o) == len(x) == len(y) == len(z)
        return Coord(np.concatenate([
            o.data,
            x.unit().data,
            y.unit().data,
            z.unit().data
        ],axis=1))

    @staticmethod
    def zero(count=1) -> Coord:
        return Coord.from_nothing(count)

    @staticmethod
    def from_nothing(count=1) -> Coord:
        return Coord.from_axes(P0(count), PX(1,count), PY(1,count), PZ(1,count))

    @staticmethod
    def from_xy(origin: Point, x_axis: Point, y_axis: Point) -> Coord:
        z_axis = x_axis.cross(y_axis)
        return Coord.from_axes(origin, x_axis, z_axis.cross(x_axis), z_axis)

    @staticmethod
    def from_yz(origin: Point, y_axis: Point, z_axis: Point) -> Coord:
        x_axis = y_axis.cross(z_axis)
        return Coord.from_axes(origin, x_axis, y_axis, x_axis.cross(y_axis))

    @staticmethod
    def from_zx(origin: Point, z_axis: Point, x_axis: Point) -> Coord:
        y_axis = z_axis.cross(x_axis)
        return Coord.from_axes(origin, y_axis.cross(z_axis), y_axis, z_axis)

    def rotation_matrix(self):
        return self.data[:,3:].reshape(len(self),-3,3)

    def inverse_rotation_matrix(self):
        return Quaternion.from_rotation_matrix(self.rotation_matrix()).inverse().to_rotation_matrix()

    def rotate(self, rotation=Quaternion) -> Coord:
        return Coord.from_axes(
            self.origin,
            rotation.transform_point(self.x_axis),
            rotation.transform_point(self.y_axis),
            rotation.transform_point(self.z_axis)
        )

    def __eq__(self, other):
        return self.data == other.data

    def translate(self, point) -> Coord:
        return Coord.from_axes(self.origin + point, self.x_axis, self.y_axis, self.z_axis)

    def axes(self):
        return Point.concatenate([self.x_axis, self.y_axis, self.z_axis])

    def plot(self, fig=None, scale=1, label: str = None):
        import plotly.graph_objects as go
        if fig is None:
            fig = go.Figure(layout=dict(scene=dict(aspectmode="data")))

        if len(self) > 1:
            for c in self:
                fig = c.plot(fig)
            return fig
        fig.add_trace(
            go.Scatter3d(
                x=self.origin.x,
                y=self.origin.y,
                z=self.origin.z,
                mode="markers",
                name="Origin",
                marker=dict(size=5, color="black"),
            )
        )
        colors = ["red", "green", "blue"]
        for i, axis in enumerate([self.x_axis, self.y_axis, self.z_axis]):
            fig.add_trace(
                go.Scatter3d(
                    x=[self.origin.x[0], (self.origin.x + axis.x * scale)[0]],
                    y=[self.origin.y[0], (self.origin.y + axis.y * scale)[0]],
                    z=[self.origin.z[0], (self.origin.z + axis.z * scale)[0]],
                    mode="lines",
                    name=f"{label or 'Axis'} {Point.cols[i]}",
                    line=dict(width=2, color=colors.pop(0))
                )
            )
        return fig