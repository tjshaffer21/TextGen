import sys, hashlib, queue, threading
from time import sleep
from pathlib import Path
import tkinter as tk
from textgen import common, cmd, markov, ui

class Controller(object):
    """Controller to handle communication between model and view.

    Private Attributes
        _env (dict) : 'markov_path', 'training_path', 'model' data
        _threads (dict) : 'generate', 'train', and 'load' threads.
        _training_input (Path) : Path to training input; None if there is none.
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

    __MARKOV_PATH_STRING = 'markov_path'
    __TRAINING_PATH_STRING = 'training_path'
    __MODEL_STRING = 'model'
    __TRAIN_STRING = 'train'
    __LOAD_STRING = 'load'
    __GENERATE_STRING = 'generate'

    __GEN_BTN_STRING = 'gen_btn'
    __TRAIN_BTN_STRING = 'train_btn'

    __ERROR_OUTPUT_STRING = "ERROR"
    __INFO_OUTPUT_STRING = "INFO"
    __TRAINING_OUTPUT_STRING = "Training"
    __TRAIN_COMP_OUTPUT_STRING = "Training complete"
    __TRAIN_FAIL_OUTPUT_STRING = "Training failed"
    __ERR_NO_MAR_STRING = "No markov data found"
    __LOADING_OUTPUT_STRING = "Loading"
    __NEWLINE_STRING = "\n"

    def __init__(self, markov_path: Path, training_path: Path,
                 training_input: Path, lines: int = 1, is_gui: bool = True):
        self._env = { self.__MARKOV_PATH_STRING : markov_path,
                      self.__TRAINING_PATH_STRING : training_path,
                      self.__MODEL_STRING : None
        }
        self._training_input = Path(training_input) if training_input != None \
                                else None
        self._lines = lines if lines != None else 1

        self._threads = { self.__GENERATE_STRING: None,
                          self.__TRAIN_STRING: None,
                          self.__LOAD_STRING: None
        }
        self._lines_queue = queue.Queue()
        self._t_lock = threading.Lock()

        self._start_thread(self.__LOAD_STRING, self._setup_model)

        self._gui = None
        if is_gui: self._config_gui()

    def _config_gui(self):
        """Configure the GUI.

        Side Effects
            _gui is modified.
        """
        _root = tk.Tk()

        self._gui = ui.MainWidget(_root)
        self._gui.get_object(self.__GEN_BTN_STRING).config(
                                command=self.generate_callback)
        self._gui.get_object(self.__TRAIN_BTN_STRING).config(
                                command=self.train_callback)

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
            self._env[self.__MODEL_STRING] = \
                markov.read(self._env[self.__MARKOV_PATH_STRING])
        except FileNotFoundError as _:
            self._env[self.__MODEL_STRING] = markov.Markov()

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
                cmd.exit(self.__ERROR_OUTPUT_STRING + " %s" % r, -1)

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
            if not self._env[self.__TRAINING_PATH_STRING].exists():
                self._env[self.__TRAINING_PATH_STRING].touch(mode=0o666,
                                                             exist_ok=True)

            # Check if hash exists
            hash_obj = hashlib.md5()
            if not common.hash_exists(training_path,
                                      common.hash_file(hash_obj, training_input)):
                model.train(training_input.read_text(encoding='utf-8'))
                with training_path.open('a') as f:
                    f.write(hash_obj.hexdigest() + self.__NEWLINE_STRING)

                markov.write(model, self._env[self.__MARKOV_PATH_STRING])
        except FileNotFoundError as e: raise
        finally:
            self._t_lock.release()

    def run(self):
        """Execute the controller.

        Side Effects
            Depends on actions
        """
        if self._gui is not None:
            self._gui.run()
        else:
            while self._threads[self.__LOAD_STRING].is_alive():
                sleep(5)

            if self._training_input == None:
                if self._env[self.__MODEL_STRING].is_empty():
                    cmd.exit(self.__ERROR_OUTPUT_STRING \
                             + self.__ERR_NO_MAR_STRING, -1)
            else:
                cmd.output(self.__TRAINING_OUTPUT_STRING)
                try:
                    self._train(self._env[self.__MODEL_STRING],
                                self._env[self.__TRAINING_PATH_STRING],
                                self._training_input)
                    cmd.output(self.__TRAIN_COMP_OUTPUT_STRING)
                except FileNotFoundError as e:
                    cmd.output(e)
            self._generate(self._env[self.__MODEL_STRING], self._lines,
                           self._lines_queue)
            cmd.output(self._lines_queue.get())

    def train_callback(self):
        """Train markov and report to GUI.

        Side Effects
            _gui is modified
        """
        if self._threads[self.__LOAD_STRING].is_alive():
            self._delay_call(self.__INFO_OUTPUT_STRING + self.__LOAD_STRING \
                + self.__NEWLINE_STRING, 5, self.generate_callback)
        else:
            self._gui.write(tk.END, self.__NEWLINE_STRING + self.__NEWLINE_STRING \
                + self.__TRAINING_OUTPUT_STRING + self.__NEWLINE_STRING)

            train_input = Path(self._gui.training_input.get())
            if not train_input.exists():
                self._gui.write(tk.END, self.__TRAIN_FAIL_OUTPUT_STRING \
                    + self.__NEWLINE_STRING + self.__NEWLINE_STRING)
            else:
                self._start_thread(self.__TRAIN_STRING,
                                   self._train,
                                   self._env[self.__MODEL_STRING],
                                   self._env[self.__TRAINING_PATH_STRING],
                                   train_input)

                self._threads[self.__TRAIN_STRING].join()
                self._gui.write(tk.END, self.__TRAIN_COMP_OUTPUT_STRING \
                    + self.__NEWLINE_STRING + self.__NEWLINE_STRING)

    def generate_callback(self):
        """Generate output and send it to the GUI.

        Side Effects
            _gui is modified.
            _line_queue is modified.
        """
        if self._env[self.__MODEL_STRING].is_empty():
            self._gui.write(tk.END, self.__ERROR_OUTPUT_STRING \
                + self.__ERR_NO_MAR_STRING + self.__NEWLINE_STRING)
        else:
            if self._threads[self.__LOAD_STRING].is_alive():
                self._delay_call(self.__INFO_OUTPUT_STRING + self.__LOAD_STRING \
                    + self.__NEWLINE_STRING, 5, self.generate_callback)
            else:
                self._start_thread(self.__GENERATE_STRING,
                                   self._generate,
                                   self._env[self.__MODEL_STRING],
                                   self._lines,
                                   self._lines_queue)
                self._threads[self.__GENERATE_STRING].join()
                self._gui.generate_output(self._lines_queue.get() \
                    + self.__NEWLINE_STRING + self.__NEWLINE_STRING)
