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
from .point import Point
from .base import Base
from geometry.point import PZ
import numpy as np
import numpy.typing as npt
import pandas as pd
from warnings import warn
from numbers import Number
from typing import Callable, Literal


class Quaternion(Base):
    cols=["w", "x", "y", "z"]

    @staticmethod
    def zero(count=1) -> Quaternion:
        return Quaternion(np.tile([1,0,0,0], (count,1)))

    @property
    def xyzw(self):
        return np.array([self.x, self.y, self.z, self.w]).T

    @property
    def axis(self) -> Point:
        return Point(self.data[:,1:])

    def norm(self) -> Quaternion:
        return self / abs(self)

    def conjugate(self) -> Quaternion:
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def inverse(self):
        return self.conjugate().norm()

    def __mul__(self, other: Number | Quaternion | npt.NDArray) -> Quaternion:
        if isinstance(other, Quaternion):
            a, b = Quaternion.length_check(self, Quaternion.type_check(other))
            w = a.w * b.w - a.axis.dot(b.axis)
            xyz = a.w * b.axis + b.w * a.axis + a.axis.cross(b.axis)
            return Quaternion(np.column_stack([w, xyz.data]))

        elif isinstance(other, Number):
            return Quaternion(self.data * other)
        elif isinstance(other, np.ndarray):
            return Quaternion(self.data * self._dprep(other))
                        
        raise TypeError(f"cant multiply a quaternion by a {other.__class__.__name__}")

    def __rmul__(self, other) -> Quaternion:
        #either it should have been picked up by the left hand object or it should commute
        return self * other   

    def transform_point(self, point: Point) -> Point:
        '''Transform a point by the rotation described by self'''
        a, b = Base.length_check(self, point)
        
        qdata = np.column_stack((np.zeros(len(a)), b.data))

        return (a * Quaternion(qdata) * a.inverse()).axis
  
    @staticmethod
    def from_euler(eul: Point) -> Quaternion:
        '''Create a quaternion from a Point of Euler angles order z, y, x'''
        eul = Point.type_check(eul).unwrap()
        half = eul * 0.5
        c = half.cos
        s = half.sin

        return Quaternion(
            np.array([
                c.y * c.z * c.x + s.y * s.z * s.x,
                c.y * c.z * s.x - s.y * s.z * c.x,
                s.y * c.z * c.x + c.y * s.z * s.x,
                c.y * s.z * c.x - s.y * c.z * s.x
            ]).T
        )

    def to_euler(self) -> Point:
        '''Create a Point of Euler angles order z,y,x'''
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x * self.x + self.y * self.y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (self.w * self.y - self.z * self.x)
        with np.errstate(invalid='ignore'):
            pitch = np.arcsin(sinp)
                
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y * self.y + self.z * self.z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        test = np.abs(sinp) >= 0.9999
        if len(sinp[test]) > 0:
            pitch[test] = np.copysign(np.pi / 2, sinp[test])
            yaw[test] = np.zeros(len(sinp[test]))

            roll[test] = 2* np.arctan2(self.x[test],self.w[test])
        return Point(roll, pitch, yaw)

    @staticmethod
    def from_axis_angle(axangles: Point) -> Quaternion:
        small = 1e-6
        angles = abs(axangles)

        qdat = np.tile(np.array([1.0, 0.0, 0.0, 0.0]), (len(angles), 1))

        if angles.any() >= small:
            baxangles = Point(axangles.data[angles >= small])
            bangles = angles[angles >= small]

            s = np.sin(bangles/2)
            c = np.cos(bangles/2)
            axis = baxangles / bangles

            qdat[angles >= small] = np.array([
                c, axis.x * s, axis.y * s, axis.z * s
            ]).T

        #qdat[abs(Quaternions(qdat)) < .001] = np.array([[1, 0, 0, 0]])
        return Quaternion(qdat)

    def to_axis_angle(self) -> Point:
        a = self._to_axis_angle()
        b = (-self)._to_axis_angle()

        res = a.data
        replocs = abs(a)>abs(b)
        res[replocs, :] = b.data[replocs, :]

        return Point(res)

    def _to_axis_angle(self) -> Point:
        """to a point of axis angles. must be normalized first."""
        angle = 2 * np.arccos(self.w)
        s = np.sqrt(1 - self.w**2)
        np.array(s)[np.array(s) < 1e-6] = 1.0
        with np.errstate(divide="ignore", invalid='ignore'):
            sangle = angle / s
            sangle[sangle==np.inf] = 0
            sangle[np.isnan(sangle)] = 0
        res = self.axis * sangle
        return res

    @staticmethod
    def axis_rates(q: Quaternion, qdot: Quaternion) -> Point:
        wdash = qdot * q.conjugate()
        return wdash.norm().to_axis_angle() 

    @staticmethod
    def _axis_rates(q: Quaternion, qdot: Quaternion) -> Point:
        wdash = qdot * q.conjugate()
        return wdash.norm()._to_axis_angle() 

    @staticmethod
    def body_axis_rates(q: Quaternion, qdot: Quaternion) -> Point:
        wdash = q.conjugate() * qdot
        return wdash.norm().to_axis_angle() 

    @staticmethod
    def _body_axis_rates(q: Quaternion, qdot: Quaternion) -> Point:
        wdash = q.conjugate() * qdot
        return wdash.norm()._to_axis_angle() 

    def rotate(self, rate: Point) -> Quaternion:
        return (Quaternion.from_axis_angle(rate) * self).norm()

    def body_rotate(self, rate: Point) -> Quaternion:
        return (self * Quaternion.from_axis_angle(rate)).norm()

    def diff(self, dt: Number | npt.NDArray = None) -> Point:
        """differentiate in the world frame"""
        if not pd.api.types.is_list_like(dt):
            dt = np.full(len(self), 1 if not dt else dt)
        assert len(dt) == len(self)
        dt = dt * len(dt) / (len(dt) - 1)

        ps = Quaternion._axis_rates(
            Quaternion(self.data[:-1, :]),
            Quaternion(self.data[1:, :])
        ) / dt[:-1]
        return Point(np.vstack([ps.data, ps.data[-1,:]]))

    def body_diff(self, dt: Number | npt.NDArray = None) -> Point:
        """differentiate in the body frame"""
        if not pd.api.types.is_list_like(dt):
            dt = np.full(len(self), 1 if not dt else dt)
        assert len(dt) == len(self)
        dt = dt * len(dt) / (len(dt) - 1)

        ps = Quaternion.body_axis_rates(
            Quaternion(self.data[:-1, :]),
            Quaternion(self.data[1:, :])
        ) / dt[:-1]
        return Point(np.vstack([ps.data, ps.data[-1,:]]))

    
    def to_rotation_matrix(self) -> npt.NDArray[np.float64]:
        """http://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation
        https://github.com/mortlind/pymath3d/blob/master/math3d/quaternion.py
        """
        n = self.norm()
        s, x, y, z = n.w, n.x, n.y, n.z
        x2, y2, z2 = n.x**2, n.y**2, n.z**2
        return np.array([
            [1 - 2 * (y2 + z2), 2 * x * y - 2 * s * z, 2 * s * y + 2 * x * z],
            [2 * x * y + 2 * s * z, 1 - 2 * (x2 + z2), -2 * s * x + 2 * y * z],
            [-2 * s * y + 2 * x * z, 2 * s * x + 2 * y * z, 1 - 2 * (x2 + y2)]
        ]).T

    @staticmethod
    def from_rotation_matrix(matrix: npt.NDArray[np.float64]) -> Quaternion:
        # This method assumes row-vector and postmultiplication of that vector
        m = matrix.conj().transpose()
        if m[2, 2] < 0:
            if m[0, 0] > m[1, 1]:
                t = 1 + m[0, 0] - m[1, 1] - m[2, 2]
                q = [m[1, 2] - m[2, 1], t, m[0, 1] + m[1, 0], m[2, 0] + m[0, 2]]
            else:
                t = 1 - m[0, 0] + m[1, 1] - m[2, 2]
                q = [m[2, 0] - m[0, 2], m[0, 1] +
                     m[1, 0], t, m[1, 2] + m[2, 1]]
        else:
            if m[0, 0] < -m[1, 1]:
                t = 1 - m[0, 0] - m[1, 1] + m[2, 2]
                q = [m[0, 1] - m[1, 0], m[2, 0] +
                     m[0, 2], m[1, 2] + m[2, 1], t]
            else:
                t = 1 + m[0, 0] + m[1, 1] + m[2, 2]
                q = [t, m[1, 2] - m[2, 1], m[2, 0] - m[0, 2], m[0, 1] - m[1, 0]]

        q = np.array(q).astype('float64')
        q *= 0.5 / np.sqrt(t)
        return Quaternion(*q)

    def closest_principal(self) -> Quaternion:
        eul = self.to_euler()
        rads = eul * (2 / np.pi)
        return Quaternion.from_euler(rads.round(0) * np.pi/2)

    def is_inverted(self) -> bool:
        # does the rotation reverse the Z axis?
        return np.sign(self.transform_point(PZ()).z) > 0

    def bearing(self, p: Point=None):
        if p is None:
            p = Point.X()
        return self.transform_point(p).bearing()
    
    def slerp(self, index: pd.Index | npt.NDArray = None, extrapolate:Literal["throw", "nearest"]="throw"):
        index = pd.Index(np.arange(len(self)) if index is None else index)

        assert len(index) == len(self)
        assert pd.Index(index).is_monotonic_increasing
        from rowan.interpolate import slerp
        def doslerp(ts: npt.NDArray | Number) -> Quaternion:
            starts = index.get_indexer(ts, method='ffill')
            stops = index.get_indexer(ts, method='bfill')
            
            #case interpolate match (start == stop - 1)
            odata = slerp(
                self[starts].to_numpy("xyzw"),
                self[stops].to_numpy("xyzw"),
                (ts - index[starts]) / (index[stops] - index[starts]),
                True 
            )

            #case exact match (start == stop)
            exacts = starts == stops
            odata[exacts] = self.to_numpy("xyzw")[starts[exacts]]

            #case outside range above (start == index[-1], stop== -1)
            aboves = stops==-1
            if np.any(aboves):
                if extrapolate=="throw":
                    raise Exception("Cannot slerp beyond range")
                else:
                    odata[aboves] = self.to_numpy("xyzw")[-1, :]
            #case outside range below (start == -1, stop==index[0])
            belows = starts==-1
            if np.any(belows):
                if extrapolate=="throw":
                    raise Exception("Cannot slerp beyond range")
                else:
                    odata[belows] = self.to_numpy("xyzw")[0, :]

            return Quaternion.from_numpy( odata, "xyzw")
            
        return doslerp

    
#    @staticmethod
#    def slerp(a: Quaternion, b: Quaternion):
#        """spherical linear interpolation"""
#        from rowan.interpolate import slerp
#        def doslerp(t):
#            xyzw = slerp(a.xyzw, b.xyzw, np.clip(t, 0, 1))
#            return Quaternion(xyzw[:,3], xyzw[:,0], xyzw[:,1], xyzw[:,2])
#        return doslerp

    @staticmethod
    def squad(p: Quaternion, a: Quaternion, b: Quaternion, q: Quaternion):
        from rowan.interpolate import squad
        def dosquad(t):
            xyzq = squad(p.xyzw, a.xyzw, b.xyzw, q.xyzw, np.clip(t, 0, 1))
            return Quaternion(xyzq[:,3], xyzq[:,0], xyzq[:,1], xyzq[:,2])
        return dosquad

    def plot_3d(self, size: float=3, vis:Literal["coord", "plane"]="coord"):
        from geometry import Transformation
        return Transformation(self).plot_3d(size, vis)

def Q0(count=1):
    return Quaternion.zero(count)



def Quaternions(*args, **kwargs):
    warn("Quaternions is deprecated, you can now just use Quaternion", DeprecationWarning)
    return Quaternions(*args, **kwargs)