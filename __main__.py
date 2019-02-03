#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, argparse
from pathlib import Path

from textgen import config, controller

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A text generator.")
    parser.add_argument('--training', '-t', type=str,
                        help="File to train the system on.")
    parser.add_argument('--lines', '-n', type=int,
                        help="Number of lines to generate.")
    parser.add_argument('--gui', '-g', action="store_true",
                        help="Invoke GUI")

    args = parser.parse_args()
    controller.Controller(Path(Path.cwd() / config.DATA_PATH / config.MARKOV_FILE),
                          Path(Path.cwd() / config.DATA_PATH / config.TRAIN_FILE),
                          args.training, args.lines, args.gui).run()