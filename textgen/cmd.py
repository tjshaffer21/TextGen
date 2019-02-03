import sys
from textgen import markov

def output_lines(markov: markov.Markov, lines: int = 1):
    """Run markov through terminal.

    Parameters
        markov (Markov) : Markov object.
        lines (int, default=1) : Number of lines to generate.
    """
    print(markov.generate(lines))

def output(msg: str):
    """ """
    print(msg)

def exit(reason: str, value: int):
    """Exit procedure.

    Parameters
        reason (str) : The reason for exiting.
        value (int) : Error code to supply to the system.
    """
    print(reason)
    sys.exit(value)
