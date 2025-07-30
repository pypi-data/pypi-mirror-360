from __future__ import annotations
import numpy
import typing
from . import interpolator
__all__ = ['Interpolator', 'interpolator']
class Interpolator:
    class Type:
        """
        Members:
        
          BarycentricRational
        
          CubicSpline
        
          Linear
        """
        BarycentricRational: typing.ClassVar[Interpolator.Type]  # value = <Type.BarycentricRational: 0>
        CubicSpline: typing.ClassVar[Interpolator.Type]  # value = <Type.CubicSpline: 1>
        Linear: typing.ClassVar[Interpolator.Type]  # value = <Type.Linear: 2>
        __members__: typing.ClassVar[dict[str, Interpolator.Type]]  # value = {'BarycentricRational': <Type.BarycentricRational: 0>, 'CubicSpline': <Type.CubicSpline: 1>, 'Linear': <Type.Linear: 2>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def generate_interpolator(interpolation_type: Interpolator.Type, x: numpy.ndarray[numpy.float64[m, 1]], y: numpy.ndarray[numpy.float64[m, 1]]) -> Interpolator:
        ...
    def __init__(self, interpolation_type: Interpolator.Type) -> None:
        ...
    @typing.overload
    def compute_derivative(self, x: float) -> float:
        ...
    @typing.overload
    def compute_derivative(self, x: numpy.ndarray[numpy.float64[m, 1]]) -> numpy.ndarray[numpy.float64[m, 1]]:
        ...
    @typing.overload
    def evaluate(self, x: numpy.ndarray[numpy.float64[m, 1]]) -> numpy.ndarray[numpy.float64[m, 1]]:
        ...
    @typing.overload
    def evaluate(self, x: float) -> float:
        ...
    def get_interpolation_type(self) -> Interpolator.Type:
        ...
