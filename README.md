# Textgen

A naive Markov text generator.

## Getting Started

### Prerequisites

- Python 3
  - hashlib
  - pickle
  - pathlib
  - tkinter

### Testing

``` python -m unittest discover -s textgen ```

### Running

``` python textgen ```

Withou any commandline arguments, the application launches the GUI.

``` python textgen -t [path-to-file] -n [num] ```

You can specify a training file and a number lines to generate. The results are printed to stdout.

``` python textgen -n [num] ```

Only specifying the number will generate lines based on the existing system.

## Authors

* Thomas Shaffer

## License

MIT -- see the LICENSE.md file for details