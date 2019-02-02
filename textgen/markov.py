# #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Markov Chain structure for generating text."""

from string import punctuation
from pathlib import Path
from functools import reduce
from nltk.tokenize import sent_tokenize, word_tokenize
from numpy.random import choice
from networkx import DiGraph, read_yaml, write_yaml

class Markov(object):
    """The Markov Chain object.

    Attributes
        _markov (Private, DiGraph) : The graph used for the chain.
            If there is no Markov data available then it will be an empty graph.
        _start_states (Private, list) : List of starting nodes for the chain.
    Parameters
        markov (str, default=None) : Path to existing data.
    Exception
        FileNotFoundError : If markov is not a valid file.
    """

    def __init__(self, markov = None):
        if isinstance(markov, Path):
            try:
                self._markov, self._start_states = self.read(markov)
            except FileNotFoundError as e: raise
        else:
            self._start_states = []
            self._markov = DiGraph()

    def _get_neighbors(self, node) -> list:
        """Return the list of neighbors of the given node.

        Parameters
            node : The node as passed into the graph.
        Return
            list : list of nodes that are neighbors.
        """
        return list(self._markov.neighbors(node))

    def _get_edge_weights(self, node) -> list:
        """Return a list of weights for the given node.

        Parameters
            node
        Return
            list
        """
        return [self._markov[node][x]['weight'] for x in self._markov[node]]

    def is_empty(self) -> bool:
        """Return if the Markov chain structure is empty or not.

        Return
            bool
        """
        return True if self._markov.number_of_nodes() == 0 else False

    def train(self, data: str):
        """Train the system with the given data.

        Parameters
            data (str): String to be added to the chain.
        Side Effects
            _markov, _start_states are modified.
        Return
            None
        """
        punc = ["!", ".", "?"]
        for sentence in sent_tokenize(data):
            prev = None
            for token in word_tokenize(sentence):
                if prev:
                    if self._markov.has_edge(prev, token):
                        self._markov[prev][token]['edge'] += 1
                    else:
                        self._markov.add_node(token, start=False,
                            stop=True if token in punc else False)
                        self._markov.add_edge(prev, token, edge=1)

                    # Calculate total edge weight.
                    edges = sum([self._markov[prev][neighbor]['edge']
                                for neighbor in self._get_neighbors(prev)])

                    # Re-Calculate the edge weights.
                    for neighbor in self._get_neighbors(prev):
                        self._markov[prev][neighbor]['weight'] = \
                            self._markov[prev][neighbor]['edge'] / edges
                else:
                    self._markov.add_node(token, start=True, stop=False)
                    if token not in self._start_states:
                        self._start_states.append(token)
                prev = token
        return None

    def generate(self, lines: int = 1) -> str:
        """Generate a line or lines of text.

        Parameters
            line (int)
        Return
            str
        """
        if lines <= 0: return "\n"

        chain = []
        for _ in range(0,lines):
            node = choice(self._start_states)
            while node:
                chain.append(node)
                neighbors = self._get_neighbors(node)
                if not neighbors or self._markov.node[node]['stop']:
                    break
                node = choice(neighbors, p=self._get_edge_weights(node))

        return reduce(lambda prev, word: prev + word if word in punctuation
                                                     else prev + ' ' + word,
                     chain)

    def read(self, fin: Path):
        """Read the Markov graph data from disk.

        Parameters
            fin (Path) : Path of the file to read.
        Return
            (DiGraph, []) : Tuple containing the graph and start nodes.
        Error
            FileNotFoundError
        """
        try:
            read_results : DiGraph = read_yaml(fin)
            return (read_results,
                    [node[0] for node in read_results.nodes(data=True)
                     if node[1]['start'] == True])
        except FileNotFoundError as e:
            raise e

    def write(self, fout: Path):
        """Write the Markov graph data to disk.

        Parameters
          fout (Path) : Path to read file from.
        """
        write_yaml(self._markov, fout)
