import tkinter as tk

from mouse_binding import EventHandler
from settings import *
from utils import *
# from block_manager import all

__all__ = [
    'UI',
]

class UI:
    def __init__(self, app):
        self.app = app

        root = app.root

        root.minsize(200, 200)

        root.columnconfigure(0, weight=1, minsize=200)
        root.rowconfigure([0, 2], weight=0, minsize=20)
        root.rowconfigure(1, weight=1, minsize=100)

        panelFrame = tk.Frame(master=root, bg=panelBG)
        canvasFrame = tk.Frame(master=root, bg=textBG)
        stateFrame = tk.Frame(master=root, bg=stateBG)
        canvasX = tk.Canvas(master=canvasFrame, bg=textBG)
        canvasX.pack(fill='both', expand=1)

        panelFrame.grid(row=0, column=0, sticky='nsew')
        canvasFrame.grid(row=1, column=0, sticky='nsew')
        stateFrame.grid(row=2, column=0, sticky='nsew')

        app.canvas.master = canvasX

        panelFrameButtons = [
            ('New', lambda: self.newFile()),
            ('Open...', lambda: self.open()),
            ('Save', lambda: self.save()),
            ('Save as...', lambda: self.saveAs()),
            ('Build', lambda: self.build()),
            ('Build as...', lambda: self.buildAs()),
            ('Build log', lambda: app.SF.build('', 0)),
        ] + __debug__ * [
            ('Canvas redraw', lambda: app.canvas.redraw(app.SF)),
            ('Save log', lambda: app.SF.save('', 0)),
            ('Console', lambda: self.openConsole()),
            ('Hard exit', lambda: app.root.destroy()),
        ]
        root.protocol("WM_DELETE_WINDOW", lambda: self.closeWindow())

        placeButtons(panelFrame, panelFrameButtons)

        mainMenu_tree = {
            "File": {
                "New file": lambda: self.newFile(),
                "Open file...": lambda: self.open(),
                "Save file": lambda: self.save(),
                "Save file as...": lambda: lambda: self.saveAs(),
            },
            "Build": {
                "Build": lambda: self.build(),
                "Build as...": lambda: self.buildAs(),
            },
            "Exit": lambda: self.closeWindow(),
        }
        if __debug__:
            mainMenu_tree["Debug"] = {
                "Hard exit": lambda: root.destroy(),
                "Lang": {
                    "-> python": lambda: app.SF.change_lang("python"),
                    "-> rscript": lambda: app.SF.change_lang("rscript"),
                    "-> default": lambda: app.SF.change_lang("default"),
                },
            }

        mainMenu = tk.Menu(master=root)
        createMenu(mainMenu, mainMenu_tree)
        root.config(menu=mainMenu)


        try:
            root.state('zoomed')
        except Exception:
            logger.log('Cannot zoom window (non-Windows OS)')

        eh = EventHandler(app, canvasX, app.canvas)

        app.canvas.draw(app.SF)
        app.root.title('new file')
        canvasX.bind("<Button-1>", eh.b1)
        canvasX.bind("<Button-2>", eh.b2)
        canvasX.bind("<Button-3>", eh.b3)

        canvasX.bind("<Double-Button-1>", eh.b1_double)
        canvasX.bind("<Double-Button-2>", eh.b2_double)
        canvasX.bind("<Double-Button-3>", eh.b3_double)

        canvasX.bind("<B1-Motion>", eh.b1_motion)
        canvasX.bind("<B2-Motion>", eh.b2_motion)
        canvasX.bind("<B3-Motion>", eh.b3_motion)

        canvasX.bind("<ButtonRelease-1>", eh.b1_release)
        canvasX.bind("<ButtonRelease-2>", eh.b2_release)
        canvasX.bind("<ButtonRelease-3>", eh.b3_release)

        canvasX.bind("<MouseWheel>", eh.wheel)  # for Windows, MacOS
        # for Linux # TODO: видимо это не работает, нужно почитать и починить
        canvasX.bind("<Button-4>", eh.wheel)
        canvasX.bind("<Button-5>", eh.wheel)

        canvasX.bind("<Control-3>", eh.b3_ctrl)
        canvasX.bind("<Control-ButtonRelease-3>", eh.b3_ctrl_release)

    def saveAs(self):
        app = self.app
        root = app.root
        """Обработчик кнопки save as handler of save as button"""
        fileName = tk.filedialog.SaveAs(
            root, filetypes=[("Visual script", ".vrc")]).show()
        if fileName == '':
            return
        else:
            if not fileName.endswith('.vrc'):
                fileName += '.vrc'
            app.SF.save(fileName)
            app.root.title(fileName)


    def save(self):
        app = self.app
        root = app.root
        """Обработчик кнопки save/ handler of save button"""
        if app.SF.fileName == '':
            self.saveAs()
        else:
            app.SF.save(app.SF.fileName)


    def open(self):
        app = self.app
        root = app.root
        """Обработчик кнопки open/ handler of open button"""
        fileName = tk.filedialog.Open(
            root, filetypes=[("Visual script", ".vrc")]).show()
        if fileName == '':
            return
        else:
            if not fileName.endswith('.vrc'):
                fileName += '.vrc'
            app.SF.open(fileName)
            app.canvas.draw(app.SF)
            app.root.title(fileName)


    def build(self):
        app = self.app
        root = app.root
        """Обработчик кнопки build/ handler of build button"""
        if app.SF.buildName == '':
            self.buildAs()
        else:
            app.SF.build(app.SF.buildName)


    def buildAs(self):
        app = self.app
        root = app.root
        """Обработчик кнопки build as/ handler of build as button"""
        ext = '*.*'  # '.b.'+app.SF.lang
        fileName = tk.filedialog.SaveAs(
            root, filetypes=[("Source code", ext)]).show()
        if fileName == '':
            return
        else:
            logger.log('Building to ' + fileName)
            # if not fileName.endswith(ext):
            #     fileName += ext
            app.SF.build(fileName)


    def close(self):
        app = self.app
        root = app.root
        if app.SF.closeQ():
            del app.SF
            return 1
        else:
            ans = tk.messagebox.askyesnocancel(
                "Save?",
                "Save changes?",
                parent=root
            )
            if ans is None:
                return 0
            if ans == 1:
                app.SF.save()
                del app.SF
                return 1
            if ans == 0:
                del app.SF
                return 1


    def newFile(self):
        app = self.app
        """Обработчик кнопки new file/ handler of new file button"""
        root = app.root
        raise NotImplementedError('ui.newFile: bad way, fix it')
        if self.close(app):
            app.SF = app.SourceFile()
            app.canvas.draw(app.SF)
            app.root.title('new file')


    def closeWindow(self):
        app = self.app
        root = app.root
        if self.close():
            root.destroy()


    consoleWindow = None
    def openConsole(self):
        app = self.app
        root = app.root
        def close(window, entry):
            if entry.get():
                eval(str(entry.get()))
            window.destroy()
        global consoleWindow
        if not consoleWindow:
            consoleWindow = tk.Toplevel(root)
            entry = tk.Entry(master=consoleWindow)
            entry.pack()
            entry.focus()
            consoleWindow.title('Console')
            consoleWindow.protocol(
                "WM_DELETE_WINDOW", lambda: close(consoleWindow, entry))


if __name__ == "__main__":
    print("This module is not for direct call!")
