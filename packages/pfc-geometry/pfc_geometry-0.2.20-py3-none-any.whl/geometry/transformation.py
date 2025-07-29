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
from geometry import Base, Point, Quaternion, P0, Q0, Coord

import numpy as np
from typing import Self, Literal


class Transformation(Base):
    cols = ["x", "y", "z", "rw", "rx", "ry", "rz"]

    def __init__(self, *args, **kwargs):
        if len(args) == len(kwargs) == 0:
            args = np.concatenate([P0().data,Q0().data],axis=1)
        elif len(args) == 1:
            if isinstance(args[0], Point):
                args = np.concatenate([args[0].data,Q0(len(args[0])).data],axis=1).T
            elif isinstance(args[0], Quaternion):
                args = np.concatenate([P0(len(args[0])).data,args[0].data],axis=1).T
        elif len(args) == 2:
            _q = args[0] if isinstance(args[0], Quaternion) else args[1]
            _p = args[0] if isinstance(args[0], Point) else args[1]
            assert isinstance(_q, Quaternion) and isinstance(_p, Point), f'expected a Point and a Quaternion, got a {_p.__class__.__name__} and a {_q.__class__.__name__}'
            args = np.concatenate([_p.data, _q.data], axis=1).T
        super().__init__(*args, **kwargs)

    @property
    def p(self):
        return Point(self.data[:,:3])

    @property
    def q(self):    
        return Quaternion(self.data[:,3:])

    def __getattr__(self, name):
        if name in list("xyz"):
            return getattr(self.translation, name)
        elif len(name) == 2 and name[0] == "r":
            if name[1] in list("wxyz"):
                return getattr(self.rotation, name[1])
        elif name=="pos":
            return self.translation
        elif name=="att":
            return self.rotation
        raise AttributeError(name)

    @staticmethod
    def build(p:Point, q:Quaternion):
        if len(p) == len(q):
            return Transformation(np.concatenate([
                p.data,
                q.data
            ],axis=1))
        elif len(p) == 1 and len(q) > 1:
            return Transformation.build(p.tile(len(q)), q)
        elif len(p) > 1 and len(q) >= 1:
            return Transformation.build(q.tile(len(p)))
        else:
            raise ValueError("incompatible lengths")

    @staticmethod
    def zero(count=1):
        return Transformation.build(P0(count), Q0(count))

    @property
    def translation(self) -> Point:
        return self.p

    @property
    def rotation(self) -> Quaternion:
        return self.q

    @staticmethod
    def from_coord(coord: Coord):
        return Transformation.from_coords(Coord.from_nothing(), coord)

    @staticmethod
    def from_coords(coord_a, coord_b):
        q1 = Quaternion.from_rotation_matrix(coord_b.rotation_matrix()).inverse()
        q2 = Quaternion.from_rotation_matrix(coord_a.rotation_matrix())
        return Transformation.build(
            coord_b.origin - coord_a.origin,
            -q1 * q2
        )
    
    def apply(self, oin: Point | Quaternion | Self | Coord):
        if isinstance(oin, Point):
            return self.point(oin)
        elif isinstance(oin, Quaternion):
            return self.rotate(oin)
        elif isinstance(oin, Coord):
            return self.coord(oin)
        elif isinstance(oin, self.__class__):
            return Transformation(self.apply(oin.p), self.apply(oin.q))
        

    def rotate(self, oin: Point | Quaternion):
        if isinstance(oin, Point):
            return self.q.transform_point(oin)
        elif isinstance(oin, Quaternion):
            return self.q * oin
        else:
            raise TypeError(f"expected a Point or a Quaternion, got a {oin.__class__.__name__}")

    def offset(self, p: Point | Self):
        if isinstance(p, Point):
            return Transformation(self.p + p, self.q)
        elif isinstance(p, self.__class__):
            return Transformation(self.p + p.p, self.q * p.q)
        else:
            raise TypeError(f"expected a Point or a Transformation, got a {p.__class__.__name__}")

    def translate(self, point: Point):
        return point + self.p

    def point(self, point: Point):
        return self.translate(self.rotate(point))       

    def coord(self, coord=None):
        if coord is None:
            coord = Coord.zero()
        return coord.translate(self.p).rotate(self.q)


    def to_matrix(self):
        outarr = np.identity(4).reshape(1,4,4)
        outarr[:, :3,:3] = self.rotation.to_rotation_matrix()
        outarr[:, 3,:3] = self.translation.data
        return outarr
        

    def plot(self, fig=None, size: float=3, vis:Literal["coord", "plane"]="coord"):
        import plotly.graph_objects as go
        from plotting.traces import axestrace, meshes
        if fig is None:
            import plotting.templates
            fig = go.Figure(layout=dict(template="generic3d+clean_paper"))
        if vis=="coord":
            fig.add_traces(axestrace(self, length=size))
        elif vis=="plane":
            fig.add_traces(meshes(len(self), self, scale=size))
        return fig
