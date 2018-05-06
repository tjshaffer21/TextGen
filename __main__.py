#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import hashlib
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

if __name__ == '__main__':
    gui = False # GUI Flag
    tin = None  # Training input
    gcnt = 1    # Lines generated.
    
    if len(sys.argv) == 1:
        gui = True
    else:
        if '-h' in sys.argv:
            cmd.print_help()
        if '-g' in sys.argv:
            gui = True

        try:
            idx = sys.argv.index("-t") + 1
            tin = Path(sys.argv[idx])

            if not tin.exists():
                print("Invalid training input.")
                sys.exit(-1)
        except ValueError:
            pass
        
        try:
            idx = sys.argv.index("-n") + 1
            gcnt = sys.argv[idx]
        except:
            pass

    # Setup Markov
    mpath = Path(Path.cwd() / config.DATA_PATH / config.MARKOV_FILE)
    tpath = Path(Path.cwd() / config.DATA_PATH / config.TRAIN_FILE)

    markov = markov.Markov()

    try:
        markov.deserialize(mpath)
    except FileNotFoundError as e:
        if not gui:
            print("WARN: No Markov data available.")

        parent = mpath.parent
        if not parent.exists():
            try:
                parent.mkdir()
            except FileExistsError:
                pass

    if gui:
        _root = tk.Tk()

        x = _root.winfo_screenwidth() / 2 - DEFAULT_WIDTH / 2
        y = _root.winfo_screenheight() / 2 - DEFAULT_HEIGHT / 2
        _root.geometry("%dx%d+%d+%d" % (DEFAULT_WIDTH, DEFAULT_HEIGHT, x, y))

        main = ui.MainWidget(_root, mpath, tpath, markov)
    
        main.mainloop()
    else:
        if tin == None:
            if markov.is_empty():
                print("ERR: No data available.")
            else:
                print(markov.generate(int(gcnt)))
        else:
            try:
                print("Training...")
                if not tpath.exists():
                    tpath.touch(mode=0o666, exist_ok=True)

                # Check if hash exists
                hash_obj = hashlib.md5()
                hs = common.hash_file(hash_obj, tin)

                found = common.hash_exists(tpath, hs)
                if not found:
                    markov.train(tin.read_text(encoding='utf-8'))
                    with tpath.open('a') as f:
                        f.write(hash_obj.hexdigest() + "\n")

                    markov.serialize(mpath)
                    print("Training complete.\n")
                else:
                    print("Training already completed.\n")
                    
                print(markov.generate(int(gcnt)))
            except FileNotFoundError as e:
                print(e)
                        
