import tkinter as tk

import ui
import canvas
import source_file
import mouse_binding
import text_editor

from settings import *
from utils import *

class App:
    def __init__(self):
        self.SF = source_file.SourceFile(self)
        self.mainWindow = tk.Tk()
        self.canvas = canvas.Canvas(self)
        canvas.canvas = self.canvas

        ui.ui_init(self)

        self.mainWindow.mainloop()
