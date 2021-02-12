import tkinter as tk

from PIL import Image, ImageTk

from block_manager import linkColors
from utils import *
from settings import *
from cache import Cache

__all__ = [
    'Canvas',
]

class Drawable:
    def __init__(self, canvas):
        raise Exception

    def info(self):
        raise Exception

    def __hash__(self):
        # print('hash')
        return hash(self.info())

    def __eq__(self, other):
        # print('eq')
        return self.info() == other.info()

    def update(self):
        raise Exception

    def checkblock(self, block):
        if not hasattr(block, 'SF'):
            self.deleted = 1
            return True
        return block.id in self.canvas.app.SF.object_ids

    def delete(self):
        self.canvas.master.delete(self.id)
        self.deleted = 1

    def __del__(self):
        self.delete()

class DrawableBlock(Drawable):
    tag = 'block'

    def __init__(self, canvas, block):
        self.canvas = canvas
        self.deleted = 0
        self.block = block
        self.id = canvas.master.create_image(
            0, 0,
            image=None,
            tag=self.tag,
        )
        self.update()

    def info(self): return f'block_{self.block.id}'

    def update(self):
        block = self.block
        canvas = self.canvas
        cache = canvas.cache
        x, y = canvas.scale(block.pos).tuple()
        ct = block.classname
        imgsize = max(round(canvas.viewzoom*blockR), 1)

        if not self.checkblock(block):
            self.delete()
            return

        origimage = cache.get(f'blockimage_{ct}', lambda: Image.open(f'images/{ct}.png'))

        photo_sel = cache.get(f'blockimage_{ct}_{imgsize}_sel', lambda: ImageTk.PhotoImage(
                origimage.resize(
                    [round(1.2*imgsize)]*2,
                    resample=Image.HAMMING,
                )
            )
        )
        photo_normal = cache.get(f'blockimage_{ct}_{imgsize}', lambda: ImageTk.PhotoImage(
                origimage.resize(
                    [imgsize, imgsize],
                    resample=Image.HAMMING,
                )
            )
        )

        canvas.master.itemconfig(
            self.id,
            image=photo_sel if block == canvas.handling else photo_normal,
            activeimage=photo_sel,
            state='normal',
            anchor='center',
        )
        canvas.master.coords(self.id, [x, y])




class DrawableLink(Drawable):
    tag = 'link'

    def __init__(self, canvas, begin, end):
        self.canvas = canvas
        self.deleted = 0
        self.begin = begin
        self.end = end
        self.id = canvas.master.create_line(
            0, 0, 0, 0,
            tag=self.tag,
        )
        self.update()

    def info(self): return f'link_{self.begin.id}_{self.end.id}'

    def update(self):
        canvas = self.canvas
        cache = canvas.cache

        thickness = link_width * canvas.viewzoom

        begin = self.begin
        end = self.end

        if not self.checkblock(begin) or not self.checkblock(end):
            self.delete()
            return


        p1 = canvas.scale(begin.pos)
        p2 = canvas.scale(end.pos)

        left = begin.classname
        right = end.classname
        color = None
        for key in [f'{left}_{right}', f'_{right}', f'{left}_', f'_']:
            if key in linkColors:
                color = linkColors[key]
                break


        canvas.master.itemconfig(
            self.id,
            fill=color,
            width=thickness,
            capstyle='round',
            arrow='last',
            arrowshape=(0.4 * canvas.viewzoom, 0.5 * canvas.viewzoom, 0.15 * canvas.viewzoom)
        )
        canvas.master.coords(self.id, *[*p1.tuple(), *p2.tuple()])


class DrawableText(Drawable):
    tag = 'block_text'

    def __init__(self, canvas, block):
        self.canvas = canvas
        self.deleted = 0
        self.block = block
        self.id = canvas.master.create_text(
            0, 0,
            tag=self.tag,
        )
        self.update()

    def info(self): return f'text_{self.block.id}'

    def update(self):
        # logger.log('updating text')
        block = self.block
        canvas = self.canvas
        x, y = canvas.scale(block.pos).tuple()

        if not self.checkblock(block):
            self.delete()
            return

        r = blockR * canvas.viewzoom / 2
        fontsize = max(round(font_size*canvas.viewzoom), 1)
        text = block.getSub()

        canvas.master.itemconfig(
            self.id,
            text=text,
            anchor='w',
            font="Consolas "+str(fontsize),
        )
        canvas.master.coords(self.id, *[x + 1.5 * r, y - fontsize, ])



class Canvas:
    def __init__(self, app, master=None):
        self.app = app

        self.master = master
        self.viewpos = Point(0, 0)
        self.viewzoom = 10

        self.handling = None
        self.touch = None
        self.link_creation = None

        self.objects = set()
        self.cache = Cache()


    def redraw(self, SF):
        try:
            self.master.delete("all")
        except Exception:
            print('Cannot delete all figures')

        self.draw(SF)

    def draw(self, SF):
        # tag_name = self.tag_name = "polygon"
        # self.master.tag_bind(tag_name, "<Enter>",
        #                      lambda event: self.master.config(cursor="hand2"))
        # self.master.tag_bind(tag_name, "<Leave>",
        #                      lambda event: self.master.config(cursor=""))
        """Рисует холст (блоки + линки)/ drawing canvas (blocks + links)"""
        tset = set()
        for obj in self.objects:
            if not obj.deleted:
                tset |= {obj}
            else:
                obj.delete()

        self.objects = tset


        # Линки/ Links
        for block_id, block in SF.object_ids.items():
            for child_id in block.childs:
                if child_id in SF.object_ids:
                    self.objects |= {DrawableLink(self, block, SF.object_ids[child_id])}
                else:
                    print(f'Warning: [Canvas.draw] unknown block id: {child}')
            self.objects |= {DrawableBlock(self, block)}
            self.objects |= {DrawableText(self, block)}

        if self.link_creation:
            # костыль для недоблока
            class Temp: pass
            obj = Temp()
            obj.pos = self.unscale(self.link_creation)
            obj.classname = 'creating'
            obj.id = -1
            self.objects |= {DrawableLink(self, self.handling, obj)}


        for obj in self.objects:
            obj.update()


    def scale(self, pos):
        """положение на холсте -> положение на экране/ Placement on canvas -> placement on screen"""
        return (pos - self.viewpos) * self.viewzoom

    def unscale(self, pos: Point):
        """положение на экране -> положение на холсте/ placement on screen -> placement on canvas"""
        return pos * (1 / self.viewzoom) + self.viewpos


if __name__ == "__main__":
    print("This module is not for direct call!")
