from block_manager import *

class Canvas:
    def __init__(self, app, master=None):
        self.app = app

        self.master = master
        self.viewpos = Point(0, 0)
        self.viewzoom = 10

        self.handling = None
        self.touch = None
        self.link_creation = None

    def draw(self, SF):
        """Рисует холст (блоки + линки)/ drawing canvas (blocks + links)"""
        # Очистка/Cleaning
        try:
            self.master.delete("all")  # TODO: убрать это и добавить изменение атрибутов существующих спрайтов.
        except Exception:
            print('Cannot delete all figures')
        self.master.create_rectangle(0, 0, 2000, 2000, fill=textBG)

        # Выбранный блок / Chosen block
        if self.handling:
            self.draw_block(self.handling, chosen=1)

        # Линки/ Links
        for _, block in SF.object_ids.items():
            for child in block.childs:
                if child in SF.object_ids:
                    self.draw_link(block, SF.object_ids[child])
                else:
                    print(f'Warning: [Canvas.draw] unknown block id: {child}')
        if self.link_creation:
            self.draw_link(self.handling, self.link_creation, creating=1)

        # Блоки/Blocks
        for _, block in SF.object_ids.items():
            self.draw_block(block)

        # Подписи/Subscription
        for _, block in SF.object_ids.items():
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

        if chosen:
            chosen_color = drawColors['chosen']
            r_sel = chosen_R * self.viewzoom
            self.master.create_oval(
                *[(x - r_sel), (y - r_sel), (x + r_sel), (y + r_sel)],
                fill=chosen_color,
            )
        else:
            self.master.create_oval(
                *[(x - r), (y - r), (x + r), (y + r)],
                fill=color,
                activewidth=0.1 * self.viewzoom,
            )

    def draw_block_text(self, block):
        """делает подпись блока/Making block subscription"""
        x, y = self.scale(block.pos).tuple()
        r = blockR * self.viewzoom
        fontsize = round(font_size*self.viewzoom)
        text = block.getSub()
        if fontsize:
            self.master.create_text(
                x + 1.5 * r, y - fontsize,
                text=text,
                anchor='w',
                font="Consolas "+str(fontsize),
                )

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
            length *= dist / (dist - blockR * self.viewzoom)

        if not creating:
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

        self.master.create_line(
            *[*p1.tuple(), *line_end.tuple()],
            fill=color,
            width=thickness,
            capstyle='round',
            activefill='red',
        )
        self.master.create_polygon(
            [*p2.tuple(), *p4.tuple(), *p5.tuple()],
            fill=color,
            outline='black',
            activefill='red',
        )


if __name__ == "__main__":
    print("This module is not for direct call!")
