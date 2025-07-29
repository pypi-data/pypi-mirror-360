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
import math
from geometry.base import Base
from geometry.point import Point
from typing import List, Union
import numpy.typing as npt
import numpy as np
import pandas as pd


def safecos(angledeg: Union[float, int, np.ndarray]):
    if isinstance(angledeg, float) or isinstance(angledeg, int):
        return max(np.cos(np.radians(angledeg)), 0.01)
    elif isinstance(angledeg, np.ndarray):
        return np.maximum(np.cos(np.radians(angledeg)), np.full(len(angledeg), 0.01))


erad = 6378100
LOCFAC = math.radians(erad)


class GPS(Base):
    cols = ["lat", "long", "alt"]
    # was 6378137, extra precision removed to match ardupilot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._longfac = safecos(self.lat)

    def __eq__(self, other) -> bool:
        return np.all(self.data == other.data)

    def __sub__(self, other) -> Point:
        assert isinstance(other, GPS), f'Cannot offset a GPS by a {other.__class__.__name__}'
        if len(other) == len(self):
            return Point(
                (self.lat - other.lat) * LOCFAC,
                (self.long - other.long) * LOCFAC * self._longfac,
                other.alt - self.alt
            )
        elif len(other) == 1:
            return self - GPS.full(other, len(self))
        elif len(self) == 1:
            return GPS.full(self, len(self)) - other
        else:
            raise ValueError(f"incompatible lengths for GPS sub ({len(self)}) != ({len(other)})")

    def offset(self, pin: Point):
        '''Offset by a point in NED coordinates'''
        if len(pin) == 1 and len(self) > 1:
            pin = Point.full(pin, len(self))
        elif len(self) == 1 and len(pin) > 1:
            return GPS.full(self, len(pin)).offset(pin)
        
        if not len(pin) == len(self):
            raise ValueError(f"incompatible lengths for GPS offset ({len(self)}) != ({len(pin)})")

        latb = self.lat + pin.x / LOCFAC
        return GPS(
            latb,
            self.long + pin.y / (LOCFAC * safecos(latb)),
            self.alt - pin.z
        )

    def bspline(self, index: npt.NDArray | pd.Index = None):
        
        def interpolator(i):
            ps: Point = self - self[0]
            ips = ps.bspline(index)(i)
            return self[0].offset(ips)

        return interpolator


'''
Extract from ardupilot:

// scaling factor from 1e-7 degrees to meters at equator
// == 1.0e-7 * DEG_TO_RAD * RADIUS_OF_EARTH
static constexpr float LOCATION_SCALING_FACTOR = 0.011131884502145034f;
// inverse of LOCATION_SCALING_FACTOR
static constexpr float LOCATION_SCALING_FACTOR_INV = 89.83204953368922f;

Vector3f Location::get_distance_NED(const Location &loc2) const
{
    return Vector3f((loc2.lat - lat) * LOCATION_SCALING_FACTOR,
                    (loc2.lng - lng) * LOCATION_SCALING_FACTOR * long_scale(),
                    (alt - loc2.alt) * 0.01f);
}

float Location::long_scale() const
{
    float scale = cosf(lat * (1.0e-7f * DEG_TO_RAD));
    return MAX(scale, 0.01f);
}
'''

