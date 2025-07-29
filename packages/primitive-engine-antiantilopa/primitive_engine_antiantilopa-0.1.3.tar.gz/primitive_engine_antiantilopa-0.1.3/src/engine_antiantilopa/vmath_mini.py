from math import pi, sqrt, sin, cos, atan2
from typing import Callable


class Vector2d:
    """
    Class to represent a pair of floats.
    """

    x: float
    y: float

    def __init__(self, a: float = 0, b: float = 0):
        self.x = a
        self.y = b

    @staticmethod
    def from_tuple(tpl: tuple[float, float]) -> "Vector2d":
        return Vector2d(tpl[0], tpl[1])

    def as_tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def distance(self, other: "Vector2d") -> float:
        return sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))

    def length(self) -> float:
        return sqrt((self.x ** 2) + (self.y ** 2))

    def intx(self) -> int:
        return int(self.x)

    def inty(self) -> int:
        return int(self.y)
    
    def norm(self) -> "Vector2d":
        l = self.length()
        if l == 0:
            return Vector2d(0, 0)
        return Vector2d(self.x / l, self.y / l)

    def to_angle(self) -> "Angle":
        return Angle(atan2(-self.y, self.x))

    def rounded(self, ndigits: int = None) -> "Vector2d":
        return Vector2d(round(self.x, ndigits), round(self.y, ndigits))
    
    def fast_reach_test(self, other: "Vector2d", dist: float|int) -> bool:
        divercity = (other - self)
        if not (-dist <= divercity.x <= dist and -dist <= divercity.y <= dist):
            return False
        if divercity.x**2 + divercity.y**2 > dist**2:
            return False
        return True

    def get_quarter(self) -> int:
        if self.x == 0 and self.y == 0:
            return 1
        if self.x >= 0 and self.y >= 0:
            return 1
        elif self.x <= 0 and self.y <= 0:
            return 3
        elif self.x < 0:
            return 2
        elif self.y < 0:
            return 4

    def is_in_box(self, other1: "Vector2d", other2: "Vector2d") -> bool:
        # return ((self - other1) * (other2 - other1)).getQuarter() == 1 and ((other2 - other1) * (other2 - other1) - (self - other1) * (self - other1)).getQuarter() == 1
        # that was elegant solution, but not computationaly efficient
        x1, y1 = other1.x, other1.y
        x2, y2 = other2.x, other2.y
        x1, x2 = (min(x1, x2), max(x1, x2))
        y1, y2 = (min(y1, y2), max(y1, y2))
        return (x1 <= self.x and self.x <= x2 and y1 <= self.y and self.y <= y2)

    def is_gaussean(self) -> bool:
        """
        Checks if the vector is a Gaussian vector (i.e., both coordinates are integers).
        """
        return self.x.is_integer() and self.y.is_integer()

    def __add__(self, other: "Vector2d") -> "Vector2d":
        return Vector2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2d") -> "Vector2d":
        return Vector2d(self.x - other.x, self.y - other.y)

    def __mul__(self, other: "float|Vector2d") -> "Vector2d":
        if isinstance(other, Vector2d):
            return Vector2d(self.x * other.x, self.y * other.y)
        else:
            return Vector2d(self.x * other, self.y * other)
    
    def __rmul__(self, other: "float|Vector2d") -> "Vector2d":
        if isinstance(other, Vector2d):
            return Vector2d(self.x * other.x, self.y * other.y)
        else:
            return Vector2d(self.x * other, self.y * other)
    
    def complex_multiply(self, other: "Vector2d") -> "Vector2d":
        # complex multiplying
        return Vector2d(self.x * other.x - self.y * other.y, self.y * other.x + self.x * other.y)

    def dot_multiply(self, other: "float|Vector2d") -> float:
        if isinstance(other, Vector2d):
            return self.x * other.x + self.y * other.y
        else:
            return (self.x + self.y) * other

    def __truediv__(self, other: "float|Vector2d") -> "Vector2d":
        if isinstance(other, Vector2d):
            return Vector2d(self.x / other.x, self.y / other.y)
        else:
            return Vector2d(self.x / other, self.y / other)

    def __floordiv__(self, other: "float|Vector2d") -> "Vector2d":
        if isinstance(other, Vector2d):
            return Vector2d(self.x // other.x, self.y // other.y)
        else:
            return Vector2d(self.x // other, self.y // other)
    
    def __mod__(self, other: "float|Vector2d") -> "Vector2d":
        if isinstance(other, Vector2d):
            return Vector2d(self.x % other.x, self.y % other.y)
        else:
            return Vector2d(self.x % other, self.y % other)

    def operation(self, other: "Vector2d", operation: Callable[[float, float], float]) -> "Vector2d":
        return Vector2d(operation(self.x, other.x), operation(self.y, other.y))

    def __repr__(self) -> str:  # for debugging
        return f"<{self.x}, {self.y}>"

    def __eq__(self, other: "Vector2d") -> bool:
        return (self.x == other.x and self.y == other.y)

    def __ne__(self, other: "Vector2d") -> bool:
        return (self.x != other.x or self.y != other.y)

    def __tuple__(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __getitem__(self, ind: int) -> float:
        if ind == 0:
            return self.x
        elif ind == 1:
            return self.y
        else:
            raise IndexError("Index out of range for Vector2d, only 0 and 1 are allowed")
    
    def __round__(self, ndigits: int = None) -> "Vector2d":
        return Vector2d(round(self.x, ndigits), round(self.y, ndigits))

    def __neg__(self) -> "Vector2d":
        return Vector2d(-self.x, -self.y)

class VectorRange:
    """
    Class to represent a range of vectors.
    """

    start: Vector2d
    end: Vector2d
    step: Vector2d
    steps: Vector2d

    def __init__(self, start: Vector2d, end: Vector2d, step: Vector2d = Vector2d(1, 1)) -> None:
        if not start.is_gaussean():
            raise ValueError("Start vector must be a Gaussian vector (both coordinates must be integers)")
        if not end.is_gaussean():
            raise ValueError("End vector must be a Gaussian vector (both coordinates must be integers)")
        if not step.is_gaussean():
            raise ValueError("Step vector must be a Gaussian vector (both coordinates must be integers)")
        steps = (end - start).operation(step, lambda x, y: x / y)
        if step.x < 0 or step.y < 0:
            raise ValueError("from start to end step number must be positive")
        if not steps.is_gaussean():
            raise ValueError("From start to end it have to be an integer number of steps")
        
        self.steps = steps
        self.start = start
        self.end = end
        self.step = step

    def __getitem__(self, index: int) -> Vector2d:
        if index < 0:
            raise IndexError("Index out of range for VectorRange")
        if (index >= self.steps.x * self.steps.y):
            raise IndexError("Index out of range for VectorRange")
        xsteps = index % self.steps.x
        ysteps = index // self.steps.x
        return self.start + Vector2d(xsteps * self.step.x, ysteps * self.step.y)

class Angle:
    """
    class that represent angles in radians
    """

    angle: float

    def __init__(self, angle: float = 0) -> None:
        self.angle = angle
        self.bound()

    def set(self, angle: float, is_deegre: bool = False):
        if is_deegre:
            angle = angle * pi / 180
        self.angle = angle
        self.bound()

    def get(self, is_deegre: bool = False):
        if is_deegre:
            return self.angle * 180 / pi
        return self.angle

    def bound(self):
        self.angle %= (2 * pi)

    def to_vector2d(self) -> Vector2d:
        return Vector2d(cos(self.angle), sin(self.angle))

    def __add__(self, other: "Angle") -> "Angle":
        return Angle(self.get() + other.get())

    def __sub__(self, other: "Angle") -> "Angle":
        return Angle(self.get() - other.get())

    def __repr__(self) -> str:
        return str(self.angle)

    def __float__(self) -> float:
        return self.angle
