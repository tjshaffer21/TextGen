"""Common functions across interfaces."""

from pathlib import Path
import hashlib

from textgen import config

def hash_exists(fin: Path, hashdig) -> bool:
    """Check if the hash exists i the file.

    Parameters
      fin (Path) : File to read.
      hashdig () : Digest of the hash.
    Return
      bool
    """
    with fin.open('r') as f:
        for line in f:
            if line[:-1] == str(hashdig):
                return True

    return False

def hash_file(hash_obj, fout: Path):
    """Create a hash of the file.

    Parameters
      hash_obj () The hash object
      fout (Path) : Path to file to be written.
    Return
        str : If fout was found.
        None : If fout was not found.
    """
    try:
        with fout.open('rb') as f:
            buf = f.read(config.BUF_SIZE)
            while len(buf) > 0:
                hash_obj.update(buf)
                buf = f.read(config.BUF_SIZE)
    except FileNotFoundError:
        return None
    return hash_obj.hexdigest()
