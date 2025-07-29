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
from .base import Base
from .time import Time
from . import angles as angles
from .point import *
from .quaternion import *
from .gps import GPS
from .coordinate_frame import Coord
from .transformation import Transformation
from .mass import Mass


def Euler(*args, **kwargs) -> Quaternion:
    return Quaternion.from_euler(Point(*args, **kwargs))
    

def Euldeg(*args, **kwargs) -> Quaternion:
    return Quaternion.from_euler(Point(*args, **kwargs).radians())


