
import enum
from typing import ( 
    List,
    Tuple
)

class ComparisonCondition(enum.Enum):
	LESS_THAN : ComparisonCondition 
	GREATER_THAN : ComparisonCondition 

# Shared Core Classes
class XYZ:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        """
        Initializes the XYZ with the given coordinates.

        :param x: X-coordinate.
        :param y: Y-coordinate.
        :param z: Z-coordinate.
        """
        ...

    def X(self) -> float:
        """
        Gets the X-coordinate.

        :return: X-coordinate.
        """
        ...
        
    def Y(self) -> float:
        """
        Gets the Y-coordinate.

        :return: Y-coordinate.
        """
        ...

    def Z(self) -> float:
        """
        Gets the Z-coordinate.

        :return: Z-coordinate.
        """
        ...

    def __add__(self, other: 'XYZ') -> 'XYZ':
        """
        Adds two XYZ vectors.

        :param other: Another XYZ vector.
        :return: Resulting XYZ vector.
        """
        ...

    def __sub__(self, other: 'XYZ') -> 'XYZ':
        """
        Subtracts two XYZ vectors.

        :param other: Another XYZ vector.
        :return: Resulting XYZ vector.
        """
        ...

    def __mul__(self, scalar: float) -> 'XYZ':
        """
        Multiplies XYZ vector by a scalar.

        :param scalar: Scalar value.
        :return: Resulting XYZ vector.
        """
        ...

    def __eq__(self, other: 'XYZ') -> bool:
        """
        Checks equality of two XYZ vectors.

        :param other: Another XYZ vector.
        :return: True if equal, False otherwise.
        """
        ...

    def __ne__(self, other: 'XYZ') -> bool:
        """
        Checks inequality of two XYZ vectors.

        :param other: Another XYZ vector.
        :return: True if not equal, False otherwise.
        """
        ...

    def magnitude(self) -> float:
        """
        Computes the magnitude of the XYZ vector.

        :return: Magnitude.
        """
        ...

    def __repr__(self) -> str:
        """
        String representation of the XYZ vector.

        :return: String representation.
        """
        ...

class Color:
	R : int = ...
	G : int = ...
	B : int = ...

class ColorSelection(enum.Enum):
	DEFAULT : ColorSelection 
	RED : ColorSelection 
	LIME : ColorSelection 
	BLUE : ColorSelection 
	YELLOW : ColorSelection 
	CYAN : ColorSelection 
	MAGENTA  : ColorSelection 
	GRAY : ColorSelection
	MAROON : ColorSelection 
	OLIVE : ColorSelection
	GREEN : ColorSelection 
	PURPLE : ColorSelection 
	TEAL : ColorSelection	
	NAVY : ColorSelection

class Palette(object):
	@staticmethod
	def get_color(selection: ColorSelection) -> Color: ...
	@staticmethod
	def get_specific_color(red: int, green: int, blue: int) -> Color: ...
	@staticmethod
	def are_same(c1: Color, c2: Color) -> bool: ...
