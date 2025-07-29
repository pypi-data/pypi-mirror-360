from collections.abc import Collection
import enum
from typing import Dict, Sequence, Union, overload

import HepEVD


class HitDimension(enum.IntEnum):
    """Enum to distinguish between 3D and 2D hits."""

    _member_names_: list = ['TWO_D', 'THREE_D']

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    TWO_D = 1
    """A 2D hit"""

    THREE_D = 0
    """A 3D hit"""

class HitType(enum.IntEnum):
    """
    Enum for various possible hit types. This is mostly useful for LArTPC view data.
    """

    _member_names_: list = ['GENERAL', 'TWO_D_U', 'TWO_D_V', 'TWO_D_W']

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    GENERAL = 0
    """General hit type"""

    TWO_D_U = 1
    """A 2D U View hit, from a LArTPC"""

    TWO_D_V = 2
    """A 2D V View hit, from a LArTPC"""

    TWO_D_W = 3
    """A 2D W View hit, from a LArTPC"""

class Line(Marker):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg0: Point, arg1: Point, /) -> None: ...

class Marker:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: Sequence[float], /) -> None: ...

    def set_colour(self, arg: str, /) -> None: ...

    def set_label(self, arg: str, /) -> None: ...

    def set_dim(self, arg: HitDimension, /) -> None: ...

    def set_hit_type(self, arg: HitType, /) -> None: ...

class Point(Marker):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: Sequence[float], /) -> None: ...

    @overload
    def __init__(self, arg0: Sequence[float], arg1: HitDimension, arg2: HitType, /) -> None: ...

class Position:
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg: Sequence[float], /) -> None: ...

    @property
    def x(self) -> float: ...

    @x.setter
    def x(self, arg: float, /) -> None: ...

    @property
    def y(self) -> float: ...

    @y.setter
    def y(self, arg: float, /) -> None: ...

    @property
    def z(self) -> float: ...

    @z.setter
    def z(self, arg: float, /) -> None: ...

    @property
    def dim(self) -> HitDimension: ...

    @dim.setter
    def dim(self, arg: HitDimension, /) -> None: ...

    @property
    def hitType(self) -> HitType: ...

    @hitType.setter
    def hitType(self, arg: HitType, /) -> None: ...

class Ring(Marker):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(self, arg0: Sequence[float], arg1: float, arg2: float, /) -> None: ...

def add_hit_properties(hit: Collection[float | int], properties: Dict[float | int]) -> None:
    """
    Add custom properties to a hit, via a string / double dictionary.
    The hit must be passed as a (x, y, z, energy) list or array.
    """

def add_hits(hits: Collection[Collection[float | int | HitType | HitDimension]], label: str = '') -> None:
    """
    Adds hits to the current event state.
    Hits must be passed as an (NHits, Y) list or array, with the columns being (x, y, z, energy) and two optional columns (view, dimension) for the hit type and dimension.
    The view and dimension values must be from the HepEVD.HitType and HepEVD.HitDimension enums respectively.
    """

def add_markers(markers: Collection[HepEVD.Marker]) -> None:
    """
    Adds markers to the current event state.
    Markers must be passed as a list or array of marker objects.The various marker types are Point, Line and Ring.Any required parameters (labels, colours, hit dims etc), should be applied to the underlying object.
    """

def add_mc(hits: Collection[Collection[float | int | HitType | HitDimension]], label: str = '') -> None:
    """
    Adds MC hits to the current event state.
    Hits must be passed as an (NHits, Y) list or array, with the columns being (x, y, z, energy, PDG) and two optional columns (view, dimension) for the hit type and dimension.
    The view and dimension values must be from the HepEVD.HitType and HepEVD.HitDimension enums respectively.
    """

def add_particles(particles: Collection[Collection[Collection[float | int | HitType | HitDimension]]], label: str = '') -> None:
    """
    Adds particles to the current event state.
    Particles must be passed as an (NParticles, NHits, Y) list or array, with the columns being (x, y, z, energy) and two optional columns (view, dimension) for the hit type and dimension.
    The view and dimension values must be from the HepEVD.HitType and HepEVD.HitDimension enums respectively.
    """

def is_initialised(quiet: bool = False) -> bool:
    """
    Checks if the server is initialised - i.e. does a server exists, with the geometry set?
    """

def reset_server(reset_geo: bool = False) -> None:
    """Resets the server"""

def save_state(state_name: str, min_size: int = -1, clear_on_show: bool = True) -> None:
    """Saves the current state"""

def set_config(config: dict[str, str]) -> None:
    """
    Sets any top level config options for the server.
    This can include the following:
      - show2D (default: 1)
      - show3D (default: 1)
      - disableMouseOver (default: 0)
      - hitColour (default: 'grey')
      - hitSize (default: Varies for 2D vs 3D)
      - hitTransparency (default: 1.0)
    """

def set_geometry(geometry: Union[str, Collection[Collection[float | int]]]) -> None:
    """Sets the geometry of the server"""

def set_mc_string(mc_string: object) -> None:
    """Sets the current MC interaction string"""

def set_verbose(verbose: bool) -> None:
    """Sets the verbosity of the HepEVD server"""

def start_server(start_state: int = -1, clear_on_show: bool = True) -> None:
    """Starts the HepEVD server"""
