#/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Implement the user interface for the application."""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from textgen import config

class MainWidget(ttk.Frame):
    """Main Frame widget for application.

    Attributes
      train_file (StringVar) : Variable holding path to training file.
      _master (private, Frame) : Master
      _text (private, ScrolledText) : Text widget
      _menu (private, Menu) : Menu widget
      BTN_W (private, int) : Constant for default button width.
      BTN_H (private, int) : Constant for default button height.
      ABOUT_SIZE (private, tuple) : Size used for w,h of the About subwidget.

    Parameters
        master : Parent of the Widget.
    """

    BTN_W = 5
    BTN_H = 2

    ABOUT_SIZE = (400, 150)

    def __init__(self, master):
        if master == None:
            ttk.messagebox.showerror("Error", "Unable to render screen.")
            sys.exit(-1)

        # Set up GUI
        self._master = master
        self._master.title("Text Generator")
        self._master.resizable(0,0)
        self._master.protocol('WM_DELETE_WINDOW', self._exit_callback)

        ttk.Frame.__init__(self, master)

        self.train_file = tk.StringVar()
        self.train_file.set("Training File")

        self._menu = tk.Menu(self._master)
        self._init_menu()

        # Configure layout
        width=20
        height=20
        for i in range(width+1):
            self._master.grid_columnconfigure(i, weight=1)

        for i in range(height+1):
            self._master.grid_rowconfigure(i, weight=1)

        # Create Text widget
        self._text = tk.scrolledtext.ScrolledText(self._master, wrap='word',
                                                   state="disabled")
        self._text.grid(row=0, column=0, columnspan=width)

        # Create buttons
        tk.Button(self._master, text="Browse", width=self.BTN_W,
                  height=self.BTN_H, padx=10,
                  command=self._file_callback).grid(row=1, column=width-2)
        self.train_button = tk.Button(self._master, text="Train",
                                      width=self.BTN_W, height=self.BTN_H,
                                      padx=10)
        self.gen_button = tk.Button(self._master, text="Generate",
                                    width=self.BTN_W, height=self.BTN_H,
                                    padx=10)

        self.train_button.grid(row=1, column=width-1)
        self.gen_button.grid(row=2, column=width-1)

        # Create file Entry
        ttk.Entry(self._master, width=30,
              textvariable=self.train_file).grid(row=1, column=0,
                                                  columnspan=width)

    def _init_menu(self):
        """Initialize the menu bar.

        Side Effects
          master
          _menu
        """
        # File
        file = tk.Menu(self._menu, tearoff=0)
        file.add_command(label="Exit", command=self._exit_callback)
        self._menu.add_cascade(label="File", menu=file)

        # Help
        help = tk.Menu(self._menu, tearoff=0)
        help.add_command(label="About", command=self._about_callback)
        self._menu.add_cascade(label="Help", menu=help)

        self._master.config(menu=self._menu)

    def _about_callback(self):
        """Callback for th about command."""
        about = tk.Toplevel()
        about.title("About")
        about.resizable(0,0)

        dx = self._master.winfo_width() / 2 - self.ABOUT_SIZE[0] / 2
        dy = self._master.winfo_height() / 2 - self.ABOUT_SIZE[1] / 2
        about.geometry("%dx%d+%d+%d" % (self.ABOUT_SIZE[0], self.ABOUT_SIZE[1],
                                        self._master.winfo_x() + dx,
                                        self._master.winfo_y() + dy))

        ttk.Label(about, text="Description: \n" + config.SOFTWARE_DESC + "\n\n",
                  anchor=tk.NW).pack(fill=tk.X)
        ttk.Label(about, text="Author: " + config.SOFTWARE_AUTH,
                  anchor=tk.NW).pack(fill=tk.X)
        ttk.Label(about, text="Version: " + config.SOFTWARE_VER,
                  anchor=tk.NW).pack(fill=tk.X)

        ttk.Button(about, text="Ok", command=about.destroy).pack()

    def _exit_callback(self):
        """Callback for exit procedures."""
        self._master.destroy()

    def _file_callback(self):
        """Callback for the 'Browse' button.

        Side Effects
          train_file
        """
        self.train_file.set(tk.filedialog.askopenfilename(
            initialdir = str(Path.cwd()),
            title = "Select file",
            filetypes = (("txt files", "*.txt"), ("all files", "*."))))

    def _win_hide(self, win):
        """Hide the window and return control to parent."""
        win.grab_release()
        win.withdraw()

    def generate_output(self, output: str):
        """Output message.

        Side Effects
          _text
        """
        self.write(tk.END, output + ' ')

    def write(self, position=tk.END, text=None):
        """Convience function to write to _text.

        Parameters
          position --
          text     -- String
        Side Effects
          _text
        """
        self._text.config(state=tk.NORMAL)
        self._text.insert(position, text)
        self._text.yview(tk.END)
        self._text.config(state=tk.DISABLED)
