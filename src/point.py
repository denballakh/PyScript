
__all__ = ['Point',]

class Point:
    """Класс точки-вектора/ class of a point-vector"""
    __slots__ = ['x', 'y']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(a, b):
        """a + b"""
        return Point(a.x + b.x, a.y + b.y)

    def __mul__(a, k):
        """a * k"""
        return Point(a.x * k, a.y * k)

    def __imul__(self, k):
        self.x *= k
        self.y *= k
        return self

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __ineg__(self):
        self.x *= -1
        self.y *= -1

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __idiv__(self, k):
        """a * k"""
        if k:
            self.x /= k
            self.y /= k
        else:
            self.x = 0
            self.y = 0
        return self

    def __neg__(a):
        """-a"""
        return a * (-1)

    def __sub__(a, b):
        """a - b"""
        return a + (-b)

    def __truediv__(a, k):
        """a * k"""
        if k:
            return Point(a.x / k, a.y / k)
        else:
            return Point(0, 0)

    def __str__(self):
        """str(self)"""
        return f'({self.x},{self.y})'

    def __eq__(a, b):
        """a == b"""
        return a.x == b.x and a.y == b.y

    def __lt__(a, b):
        """a < b"""
        if a.y < b.y:
            return True
        if a.y > b.y:
            return False
        return a.x < b.x

    def __bool__(self):
        return abs(self.x)>1e-5 or abs(self.y)>1e-5

    def abs(self):
        """Длина вектора/vector length"""
        return (self.x ** 2 + self.y ** 2) ** 0.5

    @staticmethod
    def fromTuple(tup):
        """Создает Point из кортежа/ create point out of tuple"""
        return Point(*tup)

    def set(self, x, y):
        self.x = x
        self.y = y
        return self

    def tuple(self):
        """Создает кортеж из Point/ create tuple out of point"""
        return self.x, self.y

    def round(self, s=1):
        """Округляет координаты до требуемой точности/ round to the necessary accuracy"""
        return Point(round(self.x / s) * s, round(self.y / s) * s)

    def swap(self):
        return Point(self.y, self.x)

    def norm(self, k=1):
        return self / (self.abs() / k)

    def dist(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def dist1(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def dist2(self, other):
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def abs1(self):
        """Длина вектора/vector length"""
        return abs(self.x) + abs(self.y)

    def abs2(self):
        """Длина вектора/vector length"""
        return max(abs(self.x), abs(self.y))

    def setInPlace(self, x, y):
        self.x = x
        self.y = y
        return self

    def sumInPlace(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def mulInPlace(self, k):
        self.x *= k
        self.y *= k
        return self

    def negInPlace(self):
        self.x *= -1
        self.y *= -1
        return self

    def subInPlace(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def divInPlace(self, k):
        """a * k"""
        if k:
            self.x /= k
            self.y /= k
        else:
            self.x = 0
            self.y = 0
        return self

    def roundInPlace(self, s=1):
        """Округляет координаты до требуемой точности/ round to the necessary accuracy"""
        self.x = round(self.x / s) * s
        self.y = round(self.y / s) * s
        return self

    def swapInPlace(self):
        """interchange x and y coordinates"""
        self.x, self.y = self.y, self.x
        return self

    def normInPlace(self):
        self.divInPlace(self.abs())
        return self

    def copy(self):
        """Make copy of the point"""
        return Point(self.x, self.y)
