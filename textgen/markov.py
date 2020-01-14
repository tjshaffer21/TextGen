# #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Markov Chain structure for generating text."""

from string import punctuation
from pathlib import Path
import pickle
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
from scipy.sparse import csr_matrix

class Markov(object):
    """The Markov object is an implementation of a Markov chain (discrete time,
        discrete and discrete state space).

    Attributes (private)
        _corpus (dict) : The corpus consists of a dictionary of dictionaries.
                         each key is a word and its value is a dictionary con-
                         sisting of proceeding words and how many times they
                         follow in the given data set.
        _init_nodes (set) : A set of words that are classified as entry nodes
                            for the Markov chain.
        _transition (matrix) : None on init; otherwise, a csr_matrix for the
                               transition probabilities.
    """

    def __init__(self):
        self._corpus = dict()
        self._init_nodes = set()
        self._transition = None

    def add_corpus(self, corpus):
        """Increase the corpus of the chain.

        Parameters
            corpus (tuple) : Element 1 is a set of entry nodes. Element 2 is a
                             dictionary of dictionaries for the corpus.

        Modified
            _init_nodes
            _corpus
        """
        self._init_nodes = self._init_nodes | corpus[0]

        for key, value in corpus[1].items():
            if key in self._corpus.keys():
                for subkey in value:
                    if subkey in self._corpus[key]:
                        self._corpus[key][subkey] += value[subkey]
                    else:
                        self._corpus[key].update(value)
            else:
                self._corpus[key] = value

    def calc_transition(self):
        """Iterate through the corpus and calculate the transition probabilities

        Modifications
            _transition is modified

        """
        indexed_keys = list(self._corpus)
        length = len(self._corpus.keys())
        matrix = []
        for value in self._corpus.values():
            row = [0]*length

            inner_length = sum(value.values())
            for (inner_key, inner_value) in value.items():
                row[indexed_keys.index(inner_key)] = inner_value / inner_length

            matrix.append(row)

        self._transition = csr_matrix(np.array(matrix))

    def is_empty(self) -> bool:
        """Return if the Markov object is empty or not.

        Returns
            bool
        """
        # If transition hasn't been performed then treat markov as empty.
        if self._transition is None:
            return True
        return False

    def generate(self, lines: int = 1) -> str:
        """Generate a series of lines.

        Parameters
            lines (int) : The number of lines to generate; defaults to 1.

        Returns
            str
        """

        def generate_line(key_cache, transition_cache, init_list):
            line = np.random.choice(init_list)
            line_step = key_cache.index(line)
            for _ in range(np.ma.size(transition_cache,0)):
                try:
                    word = np.random.choice(key_cache, p=transition_cache[line_step])

                    if word in punctuation:
                        line += word
                    else:
                        line += " " + word

                    line_step = key_cache.index(word)
                except:
                    break
            return line


        key_cache = list(self._corpus.keys())
        transition_cache = self._transition.toarray()
        init_list = list(self._init_nodes)

        return "".join([generate_line(key_cache, transition_cache, init_list)
                        + " " for _ in range(lines)])[:-1]

    def train(self, input: str):
        cleaned = preprocess(input)
        self.add_corpus(cleaned)
        self.calc_transition()


def preprocess(data: str) -> (set, dict):
    """Given a string of data clean it up to be utilized.

    Parameters
        data (str): The uncleaned data.
    Return
        tuple (set, dict): The resulting tuple contains a set of entry words,
            and a dictionary of the processed data.
    """
    corpus = dict()
    init = set()
    for word in sent_tokenize(data):
        prev = None
        for token in word_tokenize(word):
            if prev is None:
                init.add(token)

            if prev in corpus.keys():
                if token in corpus[prev].keys():
                    corpus[prev][token] += 1
                else:
                    corpus[prev][token] = 1

            if token not in corpus.keys():
                corpus[token] = dict()
            prev = token
    return (init, corpus)

def read(path: str) -> Markov:
    """Read the pickle file.

    Parameters
        path (str) : Path where the file is located.

    Return
        Markov object
    """
    return pickle.load(open(path, "rb"))

def write(obj: Markov, path: str):
    """Write the Marov object to disk.

    Parameters
        obj (Markov) : Object to write
        path (str) : Path to where to write the file.
    """
    pickle.dump(obj, open(path, "wb"))
