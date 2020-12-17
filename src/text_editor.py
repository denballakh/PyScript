import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font

from settings import *
from utils import *
import canvas
from block_manager import *


def getText(textArea):
    """Возвращает содержимое поля/ Return field containment"""
    if isinstance(textArea, tk.Entry):
        return textArea.get()
    elif isinstance(textArea, tk.Text):
        return textArea.get('1.0', 'end')[:-1]
    else:
        logger.log('Unknown type of textarea')
        return ''


class TextEditor:
    """
    Класс редактора блока/ class of the block redactor
    block - редактируемый блок/redacted block
    canvas - холст, отрисовка которого произойдет при закрытии редактора/ canvas to draw after closing redactor
    root - окно редактора/ redactor window
    panelFrame - фрейм панели кнопок/ button panel frame
    editFrame - фрейм всех полей для редактирования/ frame of redacting fields
    stateFrame - фрейм нижней строки/ frame of the lower string
    textAreas - словарь {<название поля>:<tk объект для редактирования>}/ dictionary {<field name>:<tk object>}

    """

    def __init__(self, root, block, canvas):
        self.block = block
        self.root = root
        self.canvas = canvas

        # configuring main window
        # root.minsize(400, 200)

        root.columnconfigure(0, weight=1, minsize=0)
        root.rowconfigure(0, weight=0, minsize=0)  # 20)
        root.rowconfigure(1, weight=1, minsize=0)
        root.rowconfigure(2, weight=0, minsize=20)

        # creating and placing frames
        self.panelFrame = tk.Frame(master=root, bg=panelBG)
        self.editFrame = tk.Frame(master=root)
        self.stateFrame = tk.Frame(master=root, bg=stateBG)

        # self.panelFrame.grid(row=0, column=0, sticky='nsew')
        self.editFrame.grid(row=1, column=0, sticky='nsew')
        self.stateFrame.grid(row=2, column=0, sticky='nsew')

        # Словарь со всеми полями для редактирования
        self.textAreas = {}

        focused = 0  # TODO: параметр для автофокуса
        logger.log('Block fields: ' + str(getDictValByPath(allTypes, f'{block.classname}.edit')))
        for key, val in getDictValByPath(allTypes, f'{block.classname}.edit').items():
            editing_type = val['type']
            header = val['header']
            
            if editing_type == 'invisible':
                pass
            elif editing_type == 'singleline':
                if header:
                    lbl = tk.Label(master=self.editFrame,
                                   bg=textBG, fg=textFG, text=header)
                    lbl.pack(fill='x', expand=0)

                ta = tk.Entry(master=self.editFrame, bg=textBG, fg=textFG)
                if key in block.data:
                    ta.insert(0, block.data[key])
                else:
                    logger.log(f'Wrong format of block: {block.convertToStr()}')
                ta.pack(fill='x', expand=0, side="top")

                self.textAreas[key] = ta

                if not focused:
                    ta.focus()
                    focused = 1
                    # ta.bind("Return", lambda: self.close(-1))
            elif editing_type == 'multiline':
                if header:
                    lbl = tk.Label(master=self.editFrame,
                                   bg=textBG, fg=textFG, text=header)
                    lbl.pack(fill='x', expand=0)

                ln = len(block.data[key].split('\n'))
                ta = tk.Text(master=self.editFrame, height=ln+10,
                             width=50, bg=textBG, fg=textFG, wrap='word')
                ta.insert('1.0', block.data[key])
                ta.pack(fill='both', expand=1, side="top")

                self.textAreas[key] = ta
            else:
                logger.log('Unknown type of editing field')
        stateFrameButtons = [
            ('✔ OK', lambda: self.close(1)),
            ('❌ Отмена', lambda: self.close(0)),
        ]
        placeButtons(self.stateFrame, stateFrameButtons, side='right')

        self.root.protocol("WM_DELETE_WINDOW", lambda: self.close(-1))
        self.root.title(block.getSub())


    def close(self, state=-1):
        """Закрывает редактор/closing redactor"""
        # state == -1 - спросить о закрытии и о сохранении/ ask about closing and saving
        # state == 0 - закрыть без сохранения/ close without saving
        # state == 1 - закрыть с сохранением/ close with saving
        if state == -1:
            if tk.messagebox.askyesno("close?", "Close window?", parent=self.root):
                if tk.messagebox.askyesno("save?", "Save changes?", parent=self.root):
                    state = 1
                else:
                    state = 0
            else:
                state = -1

        if state == 0:
            # не сохранить и закрыть/ don't save and close
            self.root.destroy()
            self.block.text_editor = None

        if state == 1:
            # сохраниить и закрыть/ save and close

            for key, val in getDictValByPath(allTypes, f'{self.block.classname}.edit').items():
                logger.log(f'saving key: {key}')
                if key == '<class>':
                    cn = getText(self.textAreas[key])
                    logger.log(f'changing type: {cn}')
                    if cn in allTypes:
                        self.block.changeType(cn)
                    else:
                        logger.log('Unknown type of block')
                    break
                if key in self.textAreas:
                    self.block.data[key] = getText(self.textAreas[key])
            self.root.destroy()
            self.block.text_editor = None

        self.canvas.draw(self.block.SF)


if __name__ == "__main__":
    print("This module is not for direct call!")
