import tkinter as tk

from PIL import Image, ImageTk

from block_manager import linkColors, drawColors
from utils import *
from settings import *

__all__ = [
    'Canvas',
]

class Drawable:
    def __init__(self, canvas):
        self.canvas = canvas
        pass

    def draw(self):
        pass

    def config(self):
        pass

    def coords(self):
        pass

    def delete(self):
        pass



class Canvas:
    def __init__(self, app, master=None):
        self.app = app

        self.ids = {
            'blocks': {},
            'links': {},
            'texts': {},
            'images': {},
        }

        self.master = master
        self.viewpos = Point(0, 0)
        self.viewzoom = 10

        self.handling = None
        self.touch = None
        self.link_creation = None

    def redraw(self, SF):
        # Очистка/Cleaning
        self.ids = {
            'blocks': {},
            'links': {},
            'texts': {},
            'images': {},
        }
        try:
            self.master.delete("all")  # TODO: убрать это и добавить изменение атрибутов существующих спрайтов.
        except Exception:
            print('Cannot delete all figures')

        self.draw(SF)


    def draw(self, SF):
        tag_name = self.tag_name = "polygon"
        self.master.tag_bind(tag_name, "<Enter>", lambda event: self.master.config(cursor="hand2"))
        self.master.tag_bind(tag_name, "<Leave>", lambda event: self.master.config(cursor=""))
        """Рисует холст (блоки + линки)/ drawing canvas (blocks + links)"""

        self.drawhandledblock()

        # Линки/ Links
        for block_id, block in SF.object_ids.items():
            for child_id in block.childs:
                if child_id in SF.object_ids:
                    self.draw_link(block, SF.object_ids[child_id])
                else:
                    print(f'Warning: [Canvas.draw] unknown block id: {child}')

        if self.link_creation:
            self.draw_link(self.handling, self.link_creation, creating=1)

        # Блоки/Blocks
        for block_id, block in SF.object_ids.items():
            self.draw_block(block)

        # Подписи/Subscription
        for block_id, block in SF.object_ids.items():
            self.draw_block_text(block)


    def scale(self, pos):
        """положение на холсте -> положение на экране/ Placement on canvas -> placement on screen"""
        return (pos - self.viewpos) * self.viewzoom

    def unscale(self, pos: Point):
        """положение на экране -> положение на холсте/ placement on screen -> placement on canvas"""
        return pos * (1 / self.viewzoom) + self.viewpos

    def draw_block(self, block, chosen=0):
        """Рисует блок/ Drawing block"""
        x, y = self.scale(block.pos).tuple()
        r = blockR * self.viewzoom

        ct = block.classname
        if ct in drawColors:
            color = drawColors[ct]
        else:
            color = drawColors['undefined']


        objid = block.id
        if not objid in self.ids['blocks'] or 1:
            image = Image.open(f'images/{block.classname}.png')
            image = image.resize([max(round(self.viewzoom*blockR),1), max(round(self.viewzoom*blockR),1)]
                , resample=Image.BOX
            )
            photo = ImageTk.PhotoImage(image)
            tkimage = self.master.create_image(x, y, anchor='center',image=photo, tag=self.tag_name)
            self.ids['blocks'][objid] = tkimage, photo

    def drawhandledblock(self):
        """Рисует блок/ Drawing block"""
        objid = 'selected'
        if not self.handling:
            if objid in self.ids['blocks']:
                self.master.itemconfig(self.ids['blocks'][objid], state='hidden')
                # del self.ids['blocks'][objid]
            return

        x, y = self.scale(self.handling.pos).tuple()

        chosen_color = drawColors['chosen']
        r_sel = chosen_R * self.viewzoom

        if not objid in self.ids['blocks']:
            self.ids['blocks'][objid] = self.master.create_oval(0,0,0,0)

        item = self.ids['blocks'][objid]

        self.master.itemconfig(item,
            fill=chosen_color,
            state='normal',
        )
        self.master.coords(item, *[(x - r_sel), (y - r_sel), (x + r_sel), (y + r_sel)])


    def draw_block_text(self, block):
        """делает подпись блока/Making block subscription"""
        x, y = self.scale(block.pos).tuple()
        r = blockR * self.viewzoom
        fontsize = max(round(font_size*self.viewzoom), 1)
        text = block.getSub()

        objid = block.id
        if not objid in self.ids['texts']:
            self.ids['texts'][objid] = self.master.create_text(0,0)

        item = self.ids['texts'][objid]

        self.master.itemconfig(item,
            text=text,
            anchor='w',
            font="Consolas "+str(fontsize),
        )
        self.master.coords(item, *[x + 1.5 * r, y - fontsize,])


    def draw_link(self, block, child, creating=0):
        """Рисует линк/ Drawing link"""
        p1 = self.scale(block.pos)
        thickness = link_width * self.viewzoom
        if creating:
            p2 = child
            color = linkColors['creating_']
        else:
            p2 = self.scale(child.pos)
            left = block.classname
            right = child.classname
            color = linkColors['_']
            for key in [f'{left}_{right}', f'{left}_', f'_{right}', f'_']:
                if key in linkColors:
                    color = linkColors[key]

        if p1 == p2:
            return

        dist = p1.dist(p2)

        length = arrow_length * self.viewzoom / dist
        if not creating:
            length *= dist / (dist - blockR * self.viewzoom * 0)
            dif = (blockR * self.viewzoom) / dist
            p2 += (p1 - p2) * dif


        p3 = p2 - (p2 - p1) * length

        delta = p2.copy()
        delta -= p1
        delta.y *= -1
        delta.swapInPlace()

        w = arrow_width * self.viewzoom
        # нормирование/normalizing
        n = delta.norm() * w
        p4 = p3 + n
        p5 = p3 - n

        line_end = (p4 + p5)
        line_end /= 2

        if creating:
            objid = 'creating'
        else:
            objid = f'{block.id},{child.id}'

        if not objid in self.ids['links']:
            self.ids['links'][objid] = self.master.create_line(0,0,0,0)

        item = self.ids['links'][objid]

        self.master.itemconfig(item,
            fill=color,
            width=thickness,
            capstyle='round',
            arrow=tk.LAST
        )
        self.master.coords(item, *[*p1.tuple(), *line_end.tuple()])

if __name__ == "__main__":
    print("This module is not for direct call!")
