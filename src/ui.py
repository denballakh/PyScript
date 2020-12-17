from mouse_binding import *
# from settings import *
# from utils import *
from block_manager import *

# canvasFrame = panelFrame = stateFrame = canvasX = mainWindow = ...
# app = ...

def saveAs(app):
    root = app.mainWindow
    """Обработчик кнопки save as handler of save as button"""
    fileName = tk.filedialog.SaveAs(
        root, filetypes=[("Visual script", ".vrc")]).show()
    if fileName == '':
        return
    else:
        if not fileName.endswith('.vrc'):
            fileName += '.vrc'
        app.SF.save(fileName)
        app.mainWindow.title(fileName)


def save(app):
    root = app.mainWindow
    """Обработчик кнопки save/ handler of save button"""
    if app.SF.fileName == '':
        saveAs(app)
    else:
        app.SF.save(app.SF.fileName)


def open(app):
    root = app.mainWindow
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
        app.mainWindow.title(fileName)


def build(app):
    root = app.mainWindow
    """Обработчик кнопки build/ handler of build button"""
    if app.SF.buildName == '':
        buildAs(app)
    else:
        app.SF.build(app.SF.buildName)


def buildAs(app):
    root = app.mainWindow
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


def close(app):
    root = app.mainWindow
    if app.SF.closeQ():
        del app.SF
        return 1
    else:
        ans = tk.messagebox.askyesnocancel("Save?", "Save changes?", parent=root)
        if ans is None:
            return 0
        if ans == 1:
            app.SF.save()
            del app.SF
            return 1
        if ans == 0:
            del app.SF
            return 1


def newFile(app):
    """Обработчик кнопки new file/ handler of new file button"""
    root = app.mainWindow
    raise Exception('ui.newFile: bad way, fix it')
    if close(app):
        app.SF = app.SourceFile()
        app.canvas.draw(app.SF)
        app.mainWindow.title('new file')


def closeWindow(app):
    root = app.mainWindow
    if close(app):
        root.destroy()


consoleWindow = None
def openConsole(app):
    root = app.mainWindow
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


def ui_init(app_p):
    """Инициализирует UI: кнопки + обработчики/ initialize user interface: buttons + handlers"""
    global canvasFrame, panelFrame, stateFrame, canvasX, mainWindow, chosen, app
    app = app_p
    root = mainWindow = app.mainWindow

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
        ('New', lambda: newFile(app)),
        ('Open...', lambda: open(app)),
        ('Save', lambda: save(app)),
        ('Save as...', lambda: saveAs(app)),
        ('Build', lambda: build(app)),
        ('Build as...', lambda: buildAs(app)),
        ('Build log', lambda: app.SF.build('', 0)),
    ] + __debug__ * [
            ('Canvas redraw', lambda: app.canvas.draw(app.SF)),
            ('Save log', lambda: app.SF.save('', 0)),
            ('Console', lambda: openConsole(app)),
            ('Hard exit', lambda: app.mainWindow.destroy()),
        ]
    root.protocol("WM_DELETE_WINDOW", lambda: closeWindow(app))

    placeButtons(panelFrame, panelFrameButtons)

    mainMenu_tree = {
        "File": {
            "New file": lambda: newFile(app),
            "Open file...": lambda: open(app),
            "Save file": lambda: save(app),
            "Save file as...": lambda: lambda: saveAs(app),
        },
        "Build": {
            "Build": lambda: build(app),
            "Build as...": lambda: buildAs(app),
        },
        "Exit": lambda: closeWindow(app),
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
        print('Cannot zoom window (non-Windows OS)')

    eh = EventHandler(app, canvasX, app.canvas)
    # Указываем нашему холсту на tk.Canvas, на котором он будет рисовать/ assign canvas to tk.canvas to draw on
    # assign_canvas_frame(canvasFrame)

    app.canvas.draw(app.SF)
    mainWindow.title('new file')
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
    canvasX.bind("<Button-4>", eh.wheel)  # for Linux # TODO: видимо это не работает, нужно почитать и починить
    canvasX.bind("<Button-5>", eh.wheel)  # for Linux

    canvasX.bind("<Control-3>", eh.b3_ctrl)
    canvasX.bind("<Control-ButtonRelease-3>", eh.b3_ctrl_release)


if __name__ == "__main__":
    print("This module is not for direct call!")
