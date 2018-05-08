#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Implement the Markov chain for the application."""

import string, random, re, unicodedata
import pickle
from pathlib import Path

class MarkovStruct(object):
    """Class that holds the data for each Token.

    Attributes
      _token       -- str  : The token
      _transitions -- list : List of transition tokens.
      _start       -- bool : Flag indicating token can be used at the start of a
                             sentence.
      _end         -- list : List of punctuation candidates.
    """

    def __init__(self, token: str, transitions = None):
        """Initialize the class.

        Parameters
          token       -- str
          transitions -- list : List of transition tokens.
        """
        self._token = token
        self._transitions = transitions if transitions else []
        self._end = []

        self._start = False
        self._tcount = len(self._transitions)
        self._ecount = 0

    def __str__(self):
        prestring = self._token + ": { "

        if self._transitions:
            for each in self._transitions:
                prestring += each + " "

        prestring += "} s: " + str(self._start) + ", e: " + str(self._end)

        return prestring

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._token == other._token and \
                self._transitions == other._transitions and \
                self._start == other._start and self._end == other._end

        return False

    @property
    def token(self):
        return self._token

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, s: bool):
        self._start = s

    @property
    def end(self):
        return self._end

    @property
    def ecount(self):
        return self._ecount

    @property
    def transitions(self):
        return self._transitions

    @property
    def tcount(self):
        return self._tcount

    def add_punctuation(self, punct: str):
        """Add a punctuation mark to the list.

        Parameters
          punct -- str
        """
        self._end.append(punct)
        self._ecount += 1

    def add_transitions(self, transitions):
        """Add a new set of transitions into the structure.

        Parametrs
          transitions -- str  : A single transition
                         list : A group of transitions
        """
        if isinstance(transitions, list):
            if not self._transitions:
                self._transitions = transitions
                self._tcount = len(self._transitions)
            else:
                self._transitions += transitions
            self._tcount += len(transitions)
        elif isinstance(transitions, str):
            if not self._transitions:
                self._transitions = [transitions]
            else:
                self._transitions.append(transitions)
            self._tcount += 1

class Markov(object):
    """Class that handles the Markov Chain.

    Attributes
      _markov -- Markov data stored here.
    """

    END_CHARS = ['!', '?', '.']

    def __init__(self, markov = None):
        """Initialize the class.

        Parameters
          markov -- Path to markov data.
        """
        self._markov = dict()
        if not markov:
            self.read_markov(markov)

        random.seed()

    def __iter__(self):
        return iter(self._markov)

    def __getitem__(self, key):
        return self._markov[key]

    def _get_nth_key(self, d, pos=0):
        """Return key at nth position.

        Parameters
          d   -- dict
          pos -- int
        """
        if pos < 0:
            pos += len(d)

        for i, key in enumerate(d.keys()):
            if i == pos:
                return key

        return None

    @staticmethod
    def is_start(prev, check: str) -> bool:
        """Check if word is the start of a sentence.

        Parameters
          prev  -- str : Token of previous world
          check -- str : Word to be checke.
        Return
          bool
        """
        return (not prev) or (not prev[-1:].isalpha())

    @staticmethod
    def is_end(check: str) -> bool:
        """Check if word is at the end of a sentence.

        Parameters
          check -- str: Token to examine.
        Return
          bool
        """
        build = ''.join(str(e) + "|" for e in Markov.END_CHARS)
        comp = re.compile(r'[%s]$' % build)

        if re.search(comp, check):
            if re.search(r'[.]{3}$', check): # Check elipsis
                return False
            return True
        return False

    @staticmethod
    def strip_front(word: str) -> str:
        """Clean up the front of the word.

        Parameters
          word -- str
        Return
          str
        """
        return re.sub(r'(\W+|[_]{1,})(?=\w+?\W{0,})', '', word)

    @staticmethod
    def strip_back(word: str, exc_list=[], until=0) -> str:
        """Clean up the back of the word.

        Exemptions can be made by including the characters in the exc_list, and
        indicating the value in the until indicator.

        Examples
          apple!!!!    ['!']  2  -> apple!!
          apple-!.     ['!']  1  -> apple!
          apple!-.!    ['!']  2  -> apple!!
          apple-!.     ['!']     -> apple


        Parameters
          word     -- str  : The word to sanitize
          exc_list -- list : List of exclusions.
          until    -- int  : Characters allowed to be saved.
        Return
          str
        """
        w = word
        if not exc_list or until == 0:
            w = re.sub(r'(\W|_{1,})', '', w)
        else:
            build = ''.join(str(e) + "|" for e in exc_list)
            comp = re.compile(r'(?!\w)(?![%s]+?)(\W|_{1,})' % build)
            w = re.sub(comp, '', w)

            if not w[-1:].isalpha(): # Last character is alpha so skip.
                for i in exc_list:
                    count = w.count(i) - until
                    for j in reversed(w):
                        if count == 0:
                            break
                        if j.isalpha():
                            break

                        if j == i:
                            w = w[:-1]
                            count -= 1
            pass
        return w

    def is_empty(self) -> bool:
        """Check if the dictionary is empty.

        Return
          bool
        """
        if len(self._markov) <= 0:
            return True
        return False

    def generate(self, lines=1) -> str:
        """Generate a specified number of random lines.

        Parameters
          lines : int
        Return
          str
        """
        if lines == 0:
            return "\n"

        dict_size = len(self._markov)

        sentence = ""
        end = False

        pos = random.randint(0, dict_size)
        key = None
        st = True
        while not end:
            try:
                if st:
                    pos = random.randint(0, dict_size)
                    key = self._get_nth_key(self._markov, pos-1)

                    if self._markov[key].start:
                        st = False
                        sentence += key.capitalize()
                else:
                    if self._markov[key].transitions:
                        pos = random.randint(0,
                                len(self._markov[key].transitions)-1)
                        key = self._markov[key].transitions[pos-1]

                        sentence += " " + key
                    if self._markov[key].end:
                        # Cut down on frequent erly ends.
                        prob = self._markov[key].ecount / \
                               (self._markov[key].ecount + \
                                self._markov[key].tcount)
                        prob = (prob * 100) * random.randint(0,100) + 10
                        if prob > 50:
                            end = True
            except KeyError:
                pass

        # Punctuate
        pos = random.randint(0, len(self._markov[key].end))
        sentence += self._markov[key].end[pos-1]

        return sentence + "\n" + self.generate(lines-1)

    def read_markov(self, fin) -> int:
        """Read the markov data into the system.

        Parameters
          fin -- str : Path to file.
        Return
          -1 -- If there is a failure in reading the file.
           1 -- Successful read.
        """
        if not fin:
            return -1

        path = Path(fin)
        try:
            if not path.exists():
                return -1
        except OSError:
            return -1

        with path.open(encoding='utf-8') as f:
            f.read_line()

        return 1

    def train(self, data: str) -> dict:
        """Take data input and feed it into the markov structure.

        Parameters
          data -- str : String of input.
        Return
          dict
        Modifed Attributes
          _markov
        """
        # Used to handle punctuation that is getting caught in the current regex
        # in strip_back()
        exc = ['-', ',', '\'']
        prev = None
        mars_list = dict()

        data = re.split(r'-{2,}|\s', data)
        idx = 0
        while idx < len(data):
            each = each_pres = data[idx]
            each = Markov.strip_front(Markov.strip_back(each, exc, 1)).lower()

            if each not in mars_list:
                mars_list[each] = MarkovStruct(each)

            if prev:
                try:
                    mars = Markov.strip_front(Markov.strip_back(prev, exc,
                                                                1)).lower()
                    mars_list[mars].add_transitions(mars_list[each].token)
                except KeyError: # Ignore any unique or malformed words.
                    pass

            if self.is_end(each_pres):
                mars_list[each].add_punctuation(each_pres[-1:])

            mars_list[each].start = True if Markov.is_start(prev, each_pres) \
                                    else False

            prev = each_pres
            idx += 1

        self._markov = mars_list
        return self._markov

    def deserialize(self, fin: Path):
        """Deserialize the data so it can be read from disk.

        Parameters
          fin -- Path : Path to the file to write.
        """
        try:
            fl = open(str(fin), "rb")
            self._markov = pickle.load(fl)
            fl.close()
        except (FileNotFoundError, EOFError) as e:
            raise e

    def serialize(self, fout: Path):
        """Serialize data so it can be written to disk.

        Parameters
          fout -- Path : Path to read file from.
        """
        try:
            if not fout.exists():
                fout.touch(mode=0o666, exist_ok=True)

            fl = open(str(fout), "wb")
            pickle.dump(self._markov, fl)
            fl.close()
        except FileNotFoundError as e:
            raise e
