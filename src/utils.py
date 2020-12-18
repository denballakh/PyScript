import json
# import os

import tkinter as tk

from settings import *

__all__ = [
    'Point',
    'Logger',

    'json_load',
    'createMenu',
    'placeButtons',
    'dictMerge',
    'getDictValByPath',
    'distance_to_line',
    'near_to_line',
    'cycle_checkout',
    'find_block_',

    'logger',
    'e',
    'pi',
]

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
        self.x = round(self.x / s) * s,
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

class Logger:
    def __init__(self):
        if __debug__:
            self.fp = None
            self.closed = 1

    def open(self, file: str):
        if __debug__:
            if not self.closed: raise Exception('Opening already opened file!')
            self.fp = open(file, 'wt')
            self.closed = 0
        return self

    def log(self, *msg):
        if __debug__:
            if self.closed: raise Exception('Logging after closing file!')
            items = [str(item) for item in msg]
            if debug_to_console:
                print(*items)
            for item in items:
                self.fp.write(item)
        return self

    def close(self):
        if __debug__:
            if not self.closed: raise Exception('Closing already closed file!')
            self.fp.close()
            self.closed = 1
        return self

    def __del__(self):
        self.close()

logger = Logger().open('logs/########.log')


def json_load(path: str):
    """Загружает json-объект из файла"""
    try:
        fp = open(path, 'rt')
        obj = json.load(fp)
        fp.close()
    except:
        logger.log(f'Error while reading ".json" file {path}. Returning None')
        return None
    return obj


def createMenu(master, tree: dict):
    """Создает меню и прикрепляет его к master/ create menu and assign it to master"""
    for key, val in tree.items():
        m = tk.Menu(master=master, tearoff=0)
        if isinstance(val, dict):
            createMenu(m, val)
        else:
            master.add_command(label=key, command=val)
            continue
        master.add_cascade(label=key, menu=m)


def placeButtons(master, buttons: list, side: str = 'left', fg=btnFG, bg=btnBG):
    """Располагает кнопки на фрейме/ place buttons on frame"""
    for btn in buttons:
        b = tk.Button(
            master=master, text=btn[0], command=btn[1], fg=btnFG, bg=btnBG)
        b.pack(side=side, padx=3, pady=3)

def takeFirst(x, y): return x
def takeSecond(x, y): return y

def normalMerge(a, b, f=None):
    """Функция слияния двух элементов/ Function of merging two elements"""
    if isinstance(a, dict) and isinstance(b, dict):
        return dictMerge(a, b)
    else:
        if a == b:
            return a
        elif f is not None:
            return f(a, b)
        else:
            raise Exception(f'Merge conflict: {a} and {b}')


def dictMerge(*dicts, f=None):
    """Соединяет несколько словарей в один/ merge s number of dictionaries into one"""
    if len(dicts) == 2:
        a, b = dicts
        res = a
        for key, val in b.items():
            if key in a:
                val2 = a[key]
                if val == val2:
                    res[key] = val
                else:
                    if isinstance(val, dict) and isinstance(val2, dict):
                        res[key] = dictMerge(val, val2)
                    elif f is not None:
                        res[key] = f(val2, val)
                    else:
                        raise Exception(f'Merge conflict: {a} and {b}')
            else:
                res[key] = val
        return res
    elif len(dicts) > 2:
        return dictMerge(dictMerge(dicts[0:2]), dicts[2:])
    elif len(dicts) == 0:
        return {}
    elif len(dicts) == 1:
        return dicts[0]


def _getDictValByPath(d: dict, path: str, err=None):
    """Возвращает значение элемента в словаре по пути к элементу
    / returns element value in dictionary by path to the element"""
    val: dict = d
    spl: list = path.split('.')
    for key in spl:
        if key in val:
            val = val[key]
        else:
            return err
    return val


def getDictValByPath(d, form, *args, braces='<>'):
    lb, rb = braces
    s = form
    for i in range(len(args) - 1, -1, -1):
        s = s.replace(f'{lb}{i + 1}{rb}', args[i])
    res = _getDictValByPath(d, s)
    if res is None:
        raise Exception(f'Cannot get dict value by path: \ndict:{d} \npath:{form} \nargs: {args}')
    return res


def distance_to_line(begin: Point, end: Point, point: Point):
    """Расстояние от отрезка (begin, end) до точки point/ distance from the segment (begin, end) to the point"""
    x1, y1 = begin.tuple()
    x2, y2 = end.tuple()
    x, y = point.tuple()
    if begin == end:
        dist = begin.dist(point)
    else:
        # A, B, C are factors of Ax+By+C=0 equation
        a = (x2 - x1)  # 1/A
        b = (y1 - y2)  # 1/B
        c = -x1 * b - y1 * a  # C/AB
        dist = (b * x + a * y + c) / (a ** 2 + b ** 2) ** 0.5
        dist = abs(dist)
    return dist


def near_to_line(begin: Point, end: Point, point: Point):
    """Проверяет близость точки прямой/ Check whether point is near to the line"""
    eps = nearToLine
    d = distance_to_line(begin, end, point)
    x1, y1 = begin.tuple()
    x2, y2 = end.tuple()
    x, y = point.tuple()

    return (d < eps) and (min(x1, x2) - eps < x < max(x1, x2) + eps) and (min(y1, y2) - eps < y < max(y1, y2) + eps)

# TODO: перенести эти функции в gp_sourcefile.py
def findCycle(SF, block, root):
    """Проверяет существование цикла ссылок/ checking existence of cycle links"""
    for id in block.childs:
        child = SF.object_ids[id]
        if child is root:
            return True
        elif findCycle(SF, child, root):
            return True
    return False


def cycle_checkout(SF, block):
    """Проверяет существование цикла ссылок/ checking existence of cycle links"""
    return findCycle(SF, block, block)


def find_block_(click, canvas, SF, mode=1):
    """Находит блок по позиции клика/ Find block by its position"""
    logger.log(f'Finding block in pos: ({click.x:4},{click.y:4})')

    def scale(pos):
        return canvas.scale(pos)

    def unscale(pos):
        return canvas.unscale(pos)

    clickpos = Point(click.x, click.y)
    sfclick = unscale(clickpos)

    for _, block in SF.object_ids.items():
        d = block.pos - sfclick
        if sfclick.dist2(block.pos) <= 0.5:
            logger.log(f'Block found: {block.convertToStr()}')
            return block

    logger.log(f'No blocks found')
    return None


# Число Эйлера и число пи/ Euler's number and pi number
e = 2.718281828459045
pi: float = 3.1415926535

if __name__ == '__main__':
    print('This module is not for direct call!')
