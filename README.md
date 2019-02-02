# Textgen

A naive Markov text generator.

## Getting Started

### Prerequisites

- Python 3
- hashlib
- pathlib
- tkinter
- networkx
- nltk
- numpy
- yaml

### Running

By default, ```python textgen``` is the same as ```python textgen -g```.

#### Command-line actions

Training can be performed by ```python textgen -t [path-to-file]```.

Output can be printed by ```python textgen -n [num]```.

## Limitations

* The application works under the assumption of good, clean data.
  * Currently, there needs to be more work to properly handle various use cases. In particular, there is not guarantee that rules for punctuation are properly followed.
  * Currently, there is no means of handling special data like dates.
* Performance issues with large amounts of data.
* The GUI has limited features.
* No way to delete or edit data.

## Authors

* Thomas Shaffer

## License

MIT -- see the LICENSE.md file for details