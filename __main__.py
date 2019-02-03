#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

from textgen import config, controller

def print_help():
    """Print the help menu."""
    print("usage: python textgen ... [-g] [-t file] [-n num] ...")
    print("Options and arguments:")
    print("-g\t: runs the graphical interface.")
    print("-t file\t: the training file.")
    print("-n num\t: the number of lines to generate.")
    print("-h\t: prints this help menu.")

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

    gcnt = 1
    try:
        idx = sys.argv.index("-n") + 1
        gcnt = sys.argv[idx]
    except:
        pass

    controller.Controller(Path(Path.cwd() / config.DATA_PATH / config.MARKOV_FILE),
                          Path(Path.cwd() / config.DATA_PATH / config.TRAIN_FILE),
                          training_in, int(gcnt), gui_flag).run()