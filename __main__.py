#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, hashlib
from pathlib import Path
import tkinter as tk

from textgen import config, common, ui, markov

DEFAULT_WIDTH = 650
DEFAULT_HEIGHT = 510

def print_help():
    """Print the help menu."""
    print("usage: python textgen ... [-g] [-t file] [-n num] ...")
    print("Options and arguments:")
    print("-g\t: runs the graphical interface.")
    print("-t file\t: the training file.")
    print("-n num\t: the number of lines to generate.")
    print("-h\t: prints this help menu.")

def setup_markov(markov_path: Path, gui_flag: bool) -> markov.Markov:
    """Create the markov object and return it.

    Parameter
        markov_path (Path): Path to Markov file.
        gui_flag (bool) : Flag indicating if running through gui or not.
    Return
        Markov
    """
    try:
        return markov.Markov(markov_path)
    except FileNotFoundError as _:
        if not gui_flag:
            print("WARN: No Markov data available.")
    return markov.Markov()

def run_gui(markov: markov.Markov, markov_path: Path, training_path: Path):
    """Initialize and enter into gui loop.

    Parameters
        markov (Markov) : Markov object
        markov_path (Path) : Path to Markov file.
        training_path (Path) : Path to training file.
    """
    _root = tk.Tk()

    x = _root.winfo_screenwidth() / 2 - DEFAULT_WIDTH / 2
    y = _root.winfo_screenheight() / 2 - DEFAULT_HEIGHT / 2
    _root.geometry("%dx%d+%d+%d" % (DEFAULT_WIDTH, DEFAULT_HEIGHT, x, y))

    main = ui.MainWidget(_root, markov, markov_path, training_path)

    main.mainloop()

def run_cmd(markov: markov.Markov, markov_path: Path, train_in: Path,
            training_path: Path, lines: int = 1):
    """Run markov through terminal.

    Parameters
        markov (Markov) : Markov object.
        markov_path (Path) : Markov file
        training_in (Path) : Path to input training file.
        training_path (Path) : Path to training hash data.
        lines (int, default=1) : Number of lines to generate.
    Exception
        FileNotFoundError
    """
    if train_in == None:
        if markov == None or markov.is_empty():
            exit("ERROR: No markov data found!\nAborting....", -1)
        else:
            print(markov.generate(int(gcnt)))
    else:
        try:
            print("Training...")
            if not training_path.exists():
                tpath.touch(mode=0o666, exist_ok=True)

            # Check if hash exists
            hash_obj = hashlib.md5()
            if not common.hash_exists(training_path,
                                      common.hash_file(hash_obj, train_in)):
                markov.train(train_in.read_text(encoding='utf-8'))
                with tpath.open('a') as f:
                    f.write(hash_obj.hexdigest() + "\n")

                markov.write(mpath)
                print("Training complete.\n")
            else:
                print("Training already completed.\n")

            print(markov.generate(lines))
        except FileNotFoundError as e:
            print(e)

def exit(reason: str, value: int):
    """Exit procedure.

    Parameters
        reason (str) : The reason for exiting.
        value (int) : Error code to supply to the system.
    """
    print(reason)
    sys.exit(value)

if __name__ == '__main__':
    gui_flag = False
    training_in = None

    if len(sys.argv) == 1:
        gui_flag = True
    else:
        if '-h' in sys.argv:
            print_help()
            sys.exit()
        if '-g' in sys.argv:
            gui_flag = True

        try:
            idx = sys.argv.index("-t") + 1
            training_in = Path(sys.argv[idx])
        except ValueError:
            pass

    mpath = Path(Path.cwd() / config.DATA_PATH / config.MARKOV_FILE)
    tpath = Path(Path.cwd() / config.DATA_PATH / config.TRAIN_FILE)
    markov = setup_markov(mpath, gui_flag)

    if gui_flag:
        run_gui(markov, mpath, tpath)
    else:
        gcnt = 1

        try:
            idx = sys.argv.index("-n") + 1
            gcnt = sys.argv[idx]
        except:
            pass

        run_cmd(markov, mpath, training_in, tpath, gcnt)
