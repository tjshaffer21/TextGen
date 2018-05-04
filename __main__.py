#!/usr/bin/env python3

from pathlib import Path
from tkinter import *
from textgen import ui

DATA_PATH = 'textgen/data/'

if __name__ == '__main__':
    _root = Tk()
    _root.geometry("650x510")
    _root.minsize(650,510)

    main = ui.MainWidget(_root, Path(Path.cwd() / DATA_PATH))
    
    main.mainloop()
