#!/usr/bin/env python3

"""Common functions across interfaces."""

import hashlib
from textgen import config

def hash_exists(fin, hashdig):
    """Check if the hash exists i the file.

    Parameters
      fin     -- File to read.
      hashdig -- Digest of the hash.
    Return
      bool
    """
    with fin.open('r') as f:
        for line in f:
            if line[:-1] == str(hashdig):
                return True

    return False

def hash_file(hash_obj, fout):
    """Create a hash of the file.

    Parameters
      hash_obj -- The hash object
      fout -- Path object to the file.
    Return
      None -- File not found
      str
    """
    try:
        with fout.open('rb') as f:
            buf = f.read(config.BUF_SIZE)
            while len(buf) > 0:
                hash_obj.update(buf)
                buf = f.read(config.BUF_SIZE)
    except FileNotFoundError as e:
        return None
    return hash_obj.hexdigest()
