#/usr/bin/env python3

import hashlib
import pickle
from pathlib import Path
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext

from . import markov

class MainWidget(Frame):
    """Main Frame widget for application.

    Attributes
      BTN_W         -- int : Constant for default button width.
      BTN_H         -- int : Constant for default button height.
      MARKOV_FILE   -- str : The file name sans path of the markov data
      TRAIN_STATE   -- str : File sans path of training hashes.
      BUF_SIZE      -- int : Buffer size for reading files.

      _file_dir     -- Path : Directory where files are located.
      _hash         --        Hash algorithm.
      _markov_path  -- Path : The markov data file.
      _markov       -- Markov
      _master       -- Frame : The parent widget.
      _text         -- Text  : Main text widget to display results.
      _train_file   -- StringVar : File path of training files to read.
      _train_path   -- Path : The training data file that stores hashes.
    """
    
    BTN_W = 5
    BTN_H = 2
    MARKOV_FILE = 'markov.dat'
    TRAIN_STATE = 'training.dat'
    BLOCKSIZE = 65536
    
    def __init__(self, master, file_dir=None):
        """Initialize the Widget.
        
        Parameters
          master    -- Parent of the Widget.
          file_path -- Path object to the markov data.
        """
        if master == None:
            messagebox.showerror("Error", "Unable to render screen.")
            sys.exit(-1)

        # Set up markov environment
        self._file_dir = file_dir

        self._markov_path = Path(file_dir / self.MARKOV_FILE)
        self._train_path = Path(file_dir / self.TRAIN_STATE)
        self._markov = markov.Markov()

        self._hash = hashlib.md5()

        # Set up GUI                
        self._master = master
        self._master.title("Text Generator")
        self._master.resizable(0,0)

        Frame.__init__(self, master)
        
        self._text = None
        
        self._train_file = StringVar()
        self._train_file.set("Training File")

        self._init_layout()
        self._init_markov()

    def _init_layout(self):
        """Initialze the layout.

        Modified Attributes
          self._text
          self._train_file
        """
        # Configure layout
        width=20
        height=20
        for i in range(width+1):
            self._master.grid_columnconfigure(i, weight=1)

        for i in range(height+1):
            self._master.grid_rowconfigure(i, weight=1)

        # Create Text widget
        self._text = scrolledtext.ScrolledText(self.master, wrap='word',
                                               state="disabled")
        self._text.grid(row=0, column=0, columnspan=width)
                
        # Create buttons
        Button(self.master, text="Browse", width=self.BTN_W, height=self.BTN_H,
               padx=10, command=self._file_callback).grid(row=1, column=width-2)
        Button(self.master, text="Train", width=self.BTN_W, 
               height=self.BTN_H, padx=10,
               command=self._train_callback).grid(row=1, column=width-1)
        Button(self.master, text="Generate", width=self.BTN_W,
               height=self.BTN_H, padx=10,
               command=self._gen_callback).grid(row=2, column=width-1)

        # Create file Entry
        Entry(self.master, width=30,
              textvariable=self._train_file).grid(row=1, column=0,
                                                  columnspan=width)
    
    def _init_markov(self):
        """Initialize markov system.

        Modified attributes
          _text
        """
        if self._markov_path is not None:
            try:
                self._markov.deserialize(self._markov_path)
            except FileNotFoundError as e:
                self._write(END, "WARN: No Markov data available.\n\n")
                
    def _file_callback(self):
        """Callback for the 'Browse' button.

        Modified Attributes
          _train_file
        """
        self._train_file.set(filedialog.askopenfilename(
            initialdir = str(Path.cwd()),
            title = "Select file",
            filetypes = (("txt files", "*.txt"), ("all files", "*."))))
        
    def _gen_callback(self):
        """Callback for the generate button.
        
        Modified Attributes
          _text
        """
        if self._markov is None:
            self._write(END, "Error: No Markov data available.\n\n")
        else:
            self._write(END, self._markov.generate())

    def _train_callback(self):
        """Callback for the 'Train' button.
        
        Modified Attributes
          _hash
          _markov
          _text
        """
        try:
            self._write(END, "Attempting to train...\n")
            train = Path(self._train_file.get())

            # Ensure training file exists.
            tfout = Path(self._train_path)
            if not tfout.exists():
                tfout.touch(mode=0o666, exist_ok=True)
            
            # Check if hash of file exists.
            hs = self._hash_file(train)
            found = False
            with tfout.open('r') as f:
                for line in f:
                    if line[:-1] == str(hs):
                        found = True

            if not found:
                self._markov.train(train.read_text(encoding='utf-8'))

                with tfout.open('a') as f:
                    f.write(hs + "\n")

                self._markov.serialize(self._markov_path)
                self._write(END, "Training complete.\n\n")
            else:
                self._write(END, "Training already completed.\n\n")
        except FileNotFoundError as e:
            messagebox.showerror("Error", e.strerror)

    def _hash_file(self, file_path=None):
        """Hash the file.

        Parameters
          file_path -- Path object to file.
        Return
          None -- If file_path is not found.
          str
        Modified Attributes
          _hash
        """
        try:
            with file_path.open('rb') as f:
                buf = f.read(self.BLOCKSIZE)
                while len(buf) > 0:
                    self._hash.update(buf)
                    buf = f.read(self.BLOCKSIZE)
        except FileNotFoundError as e:
            return None

        return self._hash.hexdigest()

    def _write(self, position=END, text=None):
        """Convience function to write to _text.

        Parameters
          position --
          text     -- String
        Modified Attributes
          _text
        """
        self._text.config(state=NORMAL)
        self._text.insert(position, text)
        self._text.yview(END)
        self._text.config(state=DISABLED)
