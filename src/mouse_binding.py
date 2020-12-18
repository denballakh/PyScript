import tkinter as tk
from random import uniform

from block import Block
import canvas
# from block_manager import *

from settings import *
from utils import *

__all__ = [
    'EventHandler',
]

class EventHandler:
    def __init__(self, app, tkCanvas, canvas):
        self.app = app
        self.tkCanvas = tkCanvas
        self.canvas = canvas

        self.descend_moving = 0


    def scale(self, pos): return self.canvas.scale(pos)

    def unscale(self, pos): return self.canvas.unscale(pos)


    def redraw(self):
        """Перерисовывает холст/ Redrawing canvas"""
        self.canvas.draw(self.app.SF)


    def find_block(self, click, mode=1):
        return find_block_(click, self.canvas, self.app.SF, mode=mode)


    """Обработчики нажатия клавиш/ Mouse and keys handlers"""


    def b1(self, click):
        """левая кнопка мыши/ left mouse button"""
        logger.log(f'(+  ): ({click.x:4},{click.y:4})')
        block = self.find_block(click)
        # установка начальной точки стрелки/setting of the initial arrow point
        if block:
            block.chosen = True
            self.canvas.handling = block
            self.canvas.link_creation = Point(click.x, click.y)
            self.canvas.touch = Point(click.x, click.y)
        self.redraw()


    def b2(self, click):
        """колесо/ wheel"""
        logger.log(f'( + ): ({click.x:4},{click.y:4})')
        clickpos = Point(click.x, click.y)
        block = self.find_block(clickpos)
        # удаление блока/block deletion
        if block:
            if tk.messagebox.askyesno(
                    "Delete?",
                    "Do you want to delete block '" + block.getSub() + "'?",
                    parent=self.tkCanvas):
                block.delete()
        # удаление линка/link deletion
        if not block:
            stop = 0
            for p in self.app.SF.object_ids:
                parent = self.app.SF.object_ids[p]
                begin = parent.pos
                for child in parent.childs:
                    end = self.app.SF.object_ids[child].pos
                    point = self.unscale(Point(click.x, click.y))
                    if near_to_line(begin, end, point):
                        parent.delLink(child)
                        stop = 1
                        break
                if stop:
                    break
        self.redraw()


    def b3(self, click):
        logger.log(f'(  +): ({click.x:4},{click.y:4})')
        block = self.find_block(click)
        # установка перемещаемого блока/set of moving block
        if block:
            block.chosen = True
            self.canvas.handling = block
            self.canvas.touch = Point(click.x, click.y)
        self.redraw()


    def b1_double(self, click):
        """левый двойной щелок/ left doubleclick"""
        logger.log(f'(:  ): ({click.x:4},{click.y:4})')
        block = self.find_block(click)
        clickpos = Point(click.x, click.y)
        # открытие редактора/opening redactor
        block_round = self.find_block(self.scale(self.unscale(clickpos).round()))
        if block:
            if not block.text_editor:
                block.edit(tk.Toplevel(self.tkCanvas), self.canvas)
        # создание блока/ creating block
        if not block:
            if not block_round:
                block = Block(self.app.SF)
                block.pos = self.unscale(clickpos).round()
                if openEditorAfterCreating:
                    block.edit(tk.Toplevel(self.tkCanvas), self.canvas)

        self.redraw()


    def b2_double(self, click):
        """двойной щелчок колесом/wheel doubleclick"""
        logger.log(f'( : ): ({click.x:4},{click.y:4})')
        ...
        self.redraw()


    def b3_double(self, click):
        """правый двойной щелчок/ right doubleclick"""
        logger.log(f'(  :): ({click.x:4},{click.y:4})')

        self.redraw()


    def b1_motion(self, click):
        """движение с зажатой левой клавишей/ movement with pressed left button"""
        logger.log(f'(^  ): ({click.x:4},{click.y:4})')
        # сдвиг конца стрелки/ arrow end movement
        if self.canvas.handling:
            self.canvas.link_creation = Point(click.x, click.y)
        self.redraw()


    def b2_motion(self, click):
        """движение с зажатым колесом/ movement with pressed wheel"""
        logger.log(f'( ^ ): ({click.x:4},{click.y:4})')
        ...
        self.redraw()


    def b3_motion(self, click):
        """движение с зажатой правой клавишей/ movement with pressed right button"""
        logger.log(f'(  ^): ({click.x:4},{click.y:4})')
        # сдвиг блоков/block movement
        if self.canvas.handling:
            clickpos = Point(click.x, click.y)
            if ban_impositions:
                block = self.find_block(self.scale(self.unscale(clickpos).round()))
            else:
                block = 0

            if not block:
                newpos = self.unscale(clickpos).round()
                shift = newpos - self.canvas.handling.pos
                self.canvas.handling.shift(
                    shift, desc=self.descend_moving, shift_id=uniform(0, 1))
                self.canvas.touch = clickpos
        self.redraw()


    def b1_release(self, click):
        """отпускание левой клавиши/ release of the left button"""
        logger.log(f'(-  ): ({click.x:4},{click.y:4})')
        block = self.find_block(click)
        # создание линка/Link creation
        if self.canvas.handling:
            if block and (not block == self.canvas.handling) and (block not in self.app.canvas.handling.childs):
                block_id = None
                for obj in self.app.SF.object_ids:
                    if self.app.SF.object_ids[obj] == block:
                        block_id = obj
                if block_id is not None:
                    self.canvas.handling.addLink(block_id)
                    if cycle_checkout(self.app.SF, block):
                        self.app.canvas.handling.delLink(block_id)
                        logger.log('Cycle ban')
        self.canvas.touch = None
        self.canvas.link_creation = False
        if self.canvas.handling:
            self.canvas.handling.chosen = False
        self.canvas.handling = None
        self.redraw()


    def b2_release(self, click):
        """отпускание колеса/ release of the wheel"""
        logger.log(f'( - ): ({click.x:4},{click.y:4})')
        ...
        self.redraw()


    def b3_release(self, click):
        """отпускание правой клавиши/ release of the right button"""
        logger.log(f'(  -): ({click.x:4},{click.y:4})')
        # сброс таскаемого блока
        self.canvas.touch = None
        if self.canvas.handling:
            self.canvas.handling.chosen = False
        self.canvas.handling = None

        # копия b3_ctrl_release
        self.descend_moving = 0
        self.redraw()


    def wheel(self, click):
        click.d = 0

        logger.log(f'Old view pos: {self.canvas.viewpos}')
        if hasattr(click, 'num') and click.num != '??':
            if click.num == 4:
                click.d = 1
            elif click.num == 5:
                click.d = -1
            else:
                print(f'Invalid mouse wheel event attribute: {click}, click.num={click.num}')
                return
        elif hasattr(click, 'delta'):
            click.d = click.delta
            if click.d % 120 == 0:
                click.d /= 120
        else:
            print(f'Unknown mouse wheel event: {click}')
            return
        logger.log(f'( @ ): ({click.x:4},{click.y:4}) {round(click.d):2}')
        k = e ** (zoomSpeed * click.d)

        clickpos = Point(click.x, click.y)
        SF_pos_old = self.unscale(clickpos)
        self.canvas.viewzoom *= k
        SF_pos_new = self.unscale(clickpos)
        SF_shift = SF_pos_new - SF_pos_old
        self.canvas.viewpos -= SF_shift

        logger.log(f'Mew view pos: {self.canvas.viewpos}')
        self.redraw()


    def b3_ctrl(self, click):
        logger.log('(  +)+ctrl')
        self.descend_moving = 1
        self.b3(click)


    def b3_ctrl_release(self, click):
        logger.log('(  -)+ctrl')
        self.descend_moving = 0
        self.b3_release(click)


if __name__ == "__main__":
    print("This module is not for direct call!")
