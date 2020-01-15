#/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Implement the user interface for the application."""

import tkinter as tk
from tkinter import ttk, messagebox
import pygubu

from textgen import config

class MainWidget(pygubu.TkApplication):

  __UI_FILE = "textgen/textgen/textgen.ui"
  __TITLE_STRING = "Textgen"
  __MASTER_STRING = "master"
  __TEXT_ENTRY_STRING = "text_entry"
  __TRAINING_INPUT_STRING = "training_input"
  __MAINMENU_STRING = "mainmenu"
  __EXIT_BTN_STRING = "exit_btn"
  __ABOUT_BTN_STRING = "about_btn"
  __ABOUT_STRING = "About"
  __OKAY_STRING = "Ok"
  __DESC_STRING = "Description: "
  __AUTH_STRING = "Author: "
  __VERSION_STRING = "Version: "
  __NeWLINE_STRING = "\n"

  ABOUT_SIZE = (400, 150)

  def _create_ui(self):
    self.builder = pygubu.Builder()
    self.builder.add_from_file(self.__UI_FILE)

    self.master.title(self.__TITLE_STRING)

    self.mainwindow = self.builder.get_object(self.__MASTER_STRING, self.master)
    self.text = self.builder.get_object(self.__TEXT_ENTRY_STRING, self.master)
    self.training_input = self.builder.get_variable(self.__TRAINING_INPUT_STRING)

    self.mainmenu = menu = self.builder.get_object(self.__MAINMENU_STRING,
                                                   self.master)
    self.set_menu(menu)

    self.builder.connect_callbacks(self)

  def on_file_item_clicked(self, item_id):
    if item_id == self.__EXIT_BTN_STRING:
      self.master.quit()

  def on_help_item_clicked(self, item_id):
    if item_id == self.__ABOUT_BTN_STRING:
      self._about_callback()

  def _about_callback(self):
      """Callback for the about command."""
      about = tk.Toplevel()
      about.title(self.__ABOUT_STRING)
      about.resizable(0,0)

      dx = self.master.winfo_width() / 2 - self.ABOUT_SIZE[0] / 2
      dy = self.master.winfo_height() / 2 - self.ABOUT_SIZE[1] / 2
      about.geometry("%dx%d+%d+%d" % (self.ABOUT_SIZE[0], self.ABOUT_SIZE[1],
                                      self.master.winfo_x() + dx,
                                      self.master.winfo_y() + dy))

      ttk.Label(about,
                text=self.__DESC_STRING + self.__NeWLINE_STRING \
                     + config.SOFTWARE_DESC + self.__NeWLINE_STRING \
                     + self.__NeWLINE_STRING,
                anchor=tk.NW).pack(fill=tk.X)
      ttk.Label(about,
                text=self.__AUTH_STRING + config.SOFTWARE_AUTH,
                anchor=tk.NW).pack(fill=tk.X)
      ttk.Label(about,
                text=self.__VERSION_STRING + config.SOFTWARE_VER,
                anchor=tk.NW).pack(fill=tk.X)

      ttk.Button(about, text=self.__OKAY_STRING, command=about.destroy).pack()

  def get_object(self, object_id):
      """Return an instance of an object with the given id.

      Parameters
        object_id (str) : ID for a widget object.

      Return
        Instance of widget.
      """
      return self.builder.get_object(object_id, self.master)

  def write(self, position=tk.END, text=None):
      """Convience function to write to _text.

      Parameters
        position --
        text     -- String
      Side Effects
        text
      """
      self.text.config(state=tk.NORMAL)
      self.text.insert(position, text)
      self.text.yview(tk.END)
      self.text.config(state=tk.DISABLED)

  def generate_output(self, output: str):
      """Output message.

      Side Effects
        text
      """
      self.write(tk.END, output + ' ')
