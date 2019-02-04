import sys, hashlib, queue, threading
from time import sleep
from string import punctuation
from pathlib import Path
import tkinter as tk
from functools import reduce
from numpy.random import choice
from textgen import common, cmd, markov, ui

DEFAULT_WIDTH = 650
DEFAULT_HEIGHT = 510

class Controller(object):
    """Controller to handle communication between model and view.

    Attributes
        _env (private, dict) : 'markov_path', 'training_path', 'model' data
        _threads (private, dict) : 'generate', 'train', and 'load' threads.
        _training_input (private) : Path to training input; None if there is none.
        _lines (int, default=1) : Number of lines to print. Applicable to command
                                  line only.
        _gui : GUI variable.
    Parameters
        markov_path (Path) : Path to the markov data.
        training_path (Path) : Path to the hash data.
        training_input (Path) : Path to data to train on, if available.
        lines (int) : Number of lines to generate (cmd, only)
        is_gui (bool) : Flag indicating whether GUI or terminal.
    """
    def __init__(self, markov_path: Path, training_path: Path,
                 training_input: Path, lines: int = 1, is_gui: bool = True):
        self._env = { 'markov_path': markov_path,
                      'training_path' : training_path,
                      'model' : None
        }
        self._training_input = Path(training_input) if training_input != None \
                                else None
        self._lines = lines if lines != None else 1

        # Threading
        self._threads = { 'generate': None, 'train': None, 'load': None }
        # Queue for the results of generate thread.
        self._lines_queue = queue.Queue()
        # Lock used when training.
        self._t_lock = threading.Lock()

        self._start_thread("load", self._setup_model)

        self._gui = None
        if is_gui: self._config_gui()

    def _config_gui(self):
        """Configure the GUI.

        Side Effects
            _gui is modified.
        """
        _root = tk.Tk()

        x = _root.winfo_screenwidth() / 2 - DEFAULT_WIDTH / 2
        y = _root.winfo_screenheight() / 2 - DEFAULT_HEIGHT / 2
        _root.geometry("%dx%d+%d+%d" % (DEFAULT_WIDTH, DEFAULT_HEIGHT, x, y))

        self._gui = ui.MainWidget(_root)
        self._gui.gen_button.config(command=self.generate_callback)
        self._gui.train_button.config(command=self.train_callback)

    def _delay_call(self, message: str, time: int, func):
        """Create a timer to delay a call to a function.

        Parameters
            message (str): Output message
            time (int): Seconds to delay
            func (function): Function to call
        Side Effects
            self._gui is modified.
        """
        self._gui.write(tk.END, message)
        threading.Timer(time, func).start()

    def _generate(self, model: markov.Markov, lines: int, results: queue.Queue):
        """Generate line(s) of text.

        Parameter
            model (markov.Markov)
            lines (int)
            results (Queue)
        Side Effects
            results is modified
        """
        results.put(model.generate(lines))

    def _setup_model(self):
        """Create Markov object and return it.

        Return
            Markov
                If no markov data is found then an Markov object with no data is
                returned.
        """
        try:
            self._env['model'] = markov.Markov(self._env['markov_path'])
        except FileNotFoundError as _:
            self._env['model'] = markov.Markov()

    def _start_thread(self, name : str, target, *args, **kargs):
        """Given thread information, create and start a thread.

        Parameters
            name (str) : Name of the thread that is being reference. If thread
                does not exist then create it. Names are the names used in
                self._threads.
            target (function) : Function called with thread.
            args : Arguments to pass to function.
            karg : Keyword argumetns to pass to function.
        """
        if self._threads[name] != None and not self._threads[name].is_alive():
            self._threads[name] = None

        if self._threads[name] == None:
            try:
                self._threads[name]=threading.Thread(target=target, args=args,
                    kwargs=kargs)
                self._threads[name].daemon = True
                self._threads[name].start()
            except RuntimeError as r:
                cmd.exit("Runtime error: %s" % r, -1)

    def _train(self, model: markov.Markov, training_path: Path,
               training_input: Path):
        """Train the markov model with given data.

        Parameters
            model (markov.Markov)
            training_path (Path)
            training_input (Path)
        Side Effects
            model is modified as necessary.
        Exception
            FileNotFoundError
        """
        try:
            self._t_lock.acquire()
            if not self._env['training_path'].exists():
                self._env['training_path'].touch(mode=0o666, exist_ok=True)

            # Check if hash exists
            hash_obj = hashlib.md5()
            if not common.hash_exists(training_path,
                                      common.hash_file(hash_obj, training_input)):
                model.train(training_input.read_text(encoding='utf-8'))
                with training_path.open('a') as f:
                    f.write(hash_obj.hexdigest() + "\n")

                model.write(self._env['markov_path'])
        except FileNotFoundError as e: raise
        finally:
            self._t_lock.release()

    def run(self):
        """Execute the controller.

        Side Effects
            Depends on actions
        """
        if self._gui != None:
            self._gui.mainloop()
        else:  # TODO Handle better
            while self._threads['load'].is_alive():
                sleep(5)

            if self._training_input == None:
                if self._env['model'].is_empty():
                    cmd.exit("ERROR: No markov data found!\nAborting....", -1)
            else:
                cmd.output("Training...")
                try:
                    self._train(self._env['model'], self._env['training_path'],
                                self._training_input)
                    cmd.output("Training complete.")
                except FileNotFoundError as e:
                    cmd.output(e)
            self._generate(self._env['model'], self._lines, self._lines_queue)
            cmd.output(self._lines_queue.get())

    def train_callback(self):
        """Train markov and report to GUI.

        Side Effects
            _gui is modified
        """
        if self._threads['load'].is_alive():
            self._delay_call("INFO: Still loading...\n", 5,
                                self.train_callback)
        else:
            self._gui.write(tk.END, "\n\nAttempting to train...\n")
            train_input = Path(self._gui.train_file.get())
            if not train_input.exists():
                train_input = None
                self._gui.write(tk.END, "Training failed\n\n")
            else:
                self._start_thread("train", self._train, self._env['model'],
                    self._env['training_path'], train_input)

                # TODO Block for now.
                self._threads['train'].join()
                self._gui.write(tk.END, "Training complete.\n\n")

    def generate_callback(self):
        """Generate output and send it to the GUI.

        Side Effects
            _gui is modified.
            _line_queue is modified.
        """
        if self._threads['load'].is_alive():
            self._delay_call("INFO: Still loading...\n", 5,
                                self.generate_callback)
        else:
            self._start_thread("generate", self._generate,
                self._env['model'], self._lines, self._lines_queue)

            while self._lines_queue.qsize() != 0:
                self._gui.generate_output(self._lines_queue.get())
