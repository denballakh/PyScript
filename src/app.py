import tkinter as tk

from ui import UI
from canvas import Canvas
from source_file import SourceFile
from mouse_binding import EventHandler
from text_editor import TextEditor

from settings import *
from utils import *

class App:
    def __init__(self):
        self.root = tk.Tk()

        self.SF = SourceFile(self)
        self.canvas = Canvas(self)
        self.ui = UI(self)

        self.root.mainloop()
