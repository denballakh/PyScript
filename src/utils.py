import json
# import os

import tkinter as tk

from settings import *
from logger import logger, Logger
from point import Point

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
            master=master, text=btn[0], command=btn[1], fg=btnFG, bg=btnBG,
            cursor="hand2",
        )
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
