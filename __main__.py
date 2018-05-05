#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import tkinter as tk
from textgen import ui

DATA_PATH = 'textgen/data/'
DEFAULT_WIDTH = 650
DEFAULT_HEIGHT = 510

if __name__ == '__main__':
    _root = tk.Tk()

    x = _root.winfo_screenwidth() / 2 - DEFAULT_WIDTH /2
    y = _root.winfo_screenheight() / 2 - DEFAULT_HEIGHT / 2
    _root.geometry("%dx%d+%d+%d" % (DEFAULT_WIDTH, DEFAULT_HEIGHT, x, y))

    main = ui.MainWidget(_root, Path(Path.cwd() / DATA_PATH))
    
    main.mainloop()
