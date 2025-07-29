from __future__ import annotations  # For compatibility with Python 3.9 or higher

from NaxToPy.Core.Classes.ABQKeywords.N2PKeyword import N2PKeyword


class N2PKeywordORIENTATION(N2PKeyword):
    def __init__(self, info, dictKeywordToN2P, dictEntityToN2P):
        super().__init__(info, dictKeywordToN2P, dictEntityToN2P)

    @property
    def Name(self) -> str:
        """Orientation name"""
        return self._N2PKeyword__info.Name

    @property
    def Definition(self) -> str:
        """Type of orientation. It has three possible definitions:

        - COORDINATES: defines system with the coordinates of 3 points a, b and c (optional origin)
        - NODES: defines the system with the global ids of nodes a, b and c (optional origin)
        - OFFSET TO NODES: defines the system with the local ids of nodes a, b and c (optional origin) relative to the
          element where orientation is being used"""
        return self._N2PKeyword__info.Definition

    @property
    def System(self) -> str:
        """Type of system that it uses. There are four options:

        - RECTANGULAR: defines a Cartesian system with 3 points a, b and c. c is the origin of the system; a belongs to
          the x-axis and b lies on the XY plane.
        - CYLINDRICAL: defines a cylindrical system given two points a and b on polar axis (z)
        - SPHERICAL: defines a spherical system given a (center) and b on polar axis (z)
        - Z RECTANGULAR: defines a Cartesian system with 3 points a, b and c. c is the origin of the system; a belongs
          to the z-axis and b lies on the XZ plane.
        - USER: defines the local coordinate system in user subroutine
        """
        return self._N2PKeyword__info.System

    @property
    def PointCoordinates(self) -> dict[str, list]:
        """Dictionary with the data that defines the orientation using coordinates:
        - point a
        - point b
        - point c"""
        return {key: tuple(map(float, value)) for key, value in dict(self._N2PKeyword__info.PointCoordinates).items()}
