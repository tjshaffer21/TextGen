import hashlib
from pathlib import Path
import tkinter as tk
from textgen import common, cmd, markov, ui

DEFAULT_WIDTH = 650
DEFAULT_HEIGHT = 510

class Controller(object):
    """Controller to handle communication between model and view.

    Attributes
        _markov_path (private, Path) : Path to the Markov data.
        _training_path (private, Path) : Path to the training data.
        _training_input (private) : Path to training input; None if there is none.
        _lines (int, default=1) : Number of lines to print. Applicable to command
                                  line only.
        _is_gui (bool, default=True) : Flag for view type.
    Parameters
        See Attributes
    """

    def __init__(self, markov_path: Path, training_path: Path,
                 training_input: Path, lines: int = 1, is_gui: bool = True):
        self._markov_path = markov_path
        self._training_path = training_path
        self._training_input = Path(training_input) if training_input != None \
                                else None

        self._model = self._setup_model()
        self._lines = lines if lines != None else 0

        self._gui = None
        if is_gui: self._config_gui()

    def _setup_model(self):
        """Create Markov object and return it.

        Return
            Markov
                If no markov data is found then an Markov object with no data is
                returned.
        """
        try:
            return markov.Markov(self._markov_path)
        except FileNotFoundError as _:
            return markov.Markov()

    def _train_markov(self, training_input: Path):
        """Train the markov model with given data.

        Side Effects
            _model is modified as necessary.
        Exception
            FileNotFoundError
        """
        try:
            if not self._training_path.exists():
                self._training_path.touch(mode=0o666, exist_ok=True)

            # Check if hash exists
            hash_obj = hashlib.md5()
            if not common.hash_exists(self._training_path,
                                      common.hash_file(hash_obj, training_input)):
                self._model.train(training_input.read_text(encoding='utf-8'))
                with self._training_path.open('a') as f:
                    f.write(hash_obj.hexdigest() + "\n")

                self._model.write(self._markov_path)
        except FileNotFoundError as e:
            raise

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

    def run(self):
        """Execute the controller.

        Side Effects
            Depends on actions
        """
        if self._gui != None:
            self._gui.mainloop()
        else:
            if self._training_input == None:
                if self._model.is_empty():
                    cmd.exit("ERROR: No markov data found!\nAborting....", -1)
            else:
                cmd.output("Training...")
                try:
                    self._train_markov(self._training_input)
                    cmd.output("Training complete.")
                except FileNotFoundError as e:
                    cmd.output(e)
            cmd.output_lines(self._model, self._lines)

    def train_callback(self):
        """Train markov and report to GUI."""
        self._gui.write(tk.END, "\n\nAttempting to train...\n")

        try:
            self._train_markov(Path(self._gui.train_file.get()))
            self._gui.write(tk.END, "Training complete.\n\n")
        except FileNotFoundError as e:
            self._gui.write(tk.END, "Training failed: %s\n" % e)

    def generate_callback(self):
        """Generate output and send it to the GUI."""
        self._gui.generate_output(self._model.generate())
