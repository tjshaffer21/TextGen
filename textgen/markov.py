#!/usr/bin/env python3

import string, random
import pickle
from pathlib import Path

class MarkovStruct(object):
    """Class that holds the data for each Token.

    Attributes
      _token       -- str  : The token
      _transitions -- list : List of transition tokens.
      _start       -- bool : Flag indicating token can be used at the start of a
                             sentence.
      _end         -- bool : Flag indicating token can be used at the end of a
                             sentence.
    """

    def __init__(self, token: str, transitions = None):
        """Initialize the class.

        Parameters
          token       -- str
          transitions -- list : List of transitio tokens.
        """
        self._token = token

        if not transitions:
            self._transitions = []
        else:
            self._transitions = transitions

        # Flags
        self._start = False
        self._end = False

        random.seed()

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

    @end.setter
    def end(self,  e: bool):
        self._end = e

    @property
    def transitions(self):
        return self._transitions

    def add_transitions(self, transitions):
        """Add a new set of transitions into the structure.

        Parametrs
          transitions -- str  : A single transition
                         list : A group of transitions
        """
        if isinstance(transitions, list):
            if not self._transitions:
                self._transitions = transitions
            else:
                self._transitions += transitions
        elif isinstance(transitions, str):
            if not self._transitions:
                self._transitions = [transitions]
            else:
                self._transitions.append(transitions)

    
class Markov(object):
    """Class that handles the Markov Chain.

    Attributes
      _markov -- Markov data stored here.
    """

    PUNCTUATION = ['.', '!', '?']

    def __init__(self, markov = None):
        """Initialize the class.

        Parameters
          markov -- Path to markov data.
        """

        self._markov = dict()
        if not markov:
            self.read_markov(markov)

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
    def sanitize_word(word: str) -> str:
        """Clean up the word to make it usable for the Markov structure.

        Parameters
          word -- str : Unicode string to sanitize.
        Return
          str
        """
        w = word
        
        # Clean up the front.
        for i in w:
            if not i.isalpha():
                w = w[1:]
            else:
                break

        # Clean up the back.
        for i in reversed(w):
            if not i.isalpha():
                w = w[:-1]
            else:
                break

        return w
    
    @classmethod
    def is_start(cls, prev, check: str) -> bool:
        """Check if word is the start of a sentence.

        Parameters
          cls   -- Class object
          prev  -- str : Token of previous world
          check -- str : Word to be checke.
        Return
          boolean
        """
        if not prev:
            return True
        if not prev[-1:].isalpha():
            return True
        
        return False

    @classmethod
    def is_end(cls, check: str) -> bool:
        """Check if word is the end of the sentence.

        Parameters
          cls   -- Class object
          check -- str : Word to be checked
        Return
          boolean
        """
        if not check[-1:].isalpha():
            return True

        return False

    def generate(self, lines=1):
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

        # Find start key.
        pos = random.randint(0, dict_size)
        key = None
        while not end:
            try:
                key = self._get_nth_key(self._markov, pos-1)

                if self._markov[key].start:
                    end = True
                    sentence += key.capitalize()
                else:
                    pos = (pos + 1) % dict_size
            except KeyError:
                pass

        # Iterate
        end = False        
        while not end:
            try:
                if self._markov[key].transitions:
                    pos = random.randint(0, len(self._markov[key].transitions)-1)
                    key = self._markov[key].transitions[pos-1]

                    sentence += " " + key
                    if self._markov[key].end:
                        if random.randint(0,1) == 1:
                            end = True
            except KeyError:
                pass
            
        # Punctuate
        pos = random.randint(0, len(self.PUNCTUATION)-1)
        sentence += self.PUNCTUATION[pos]

        return sentence + " " + self.generate(lines-1)
    
    def read_markov(self, fin) -> int:
        """Read the markov data into the system.

        Parameters
          fin -- str : Path to file.
        Return
          -1 -- If there is a failure in reading the file.
           1 -- Successful read.
        """
        success = -1
        if not fin:
            return success
        
        path = Path(fin)
        if not path.exists():
            return success

        with path.open(encoding='utf-8') as f:
            f.read_line()

        success = 1
        return success
        
    def train(self, data: str) -> dict:
        """Take data input and feed it into the markov structure.

        Parameters
          data -- str : String of input.
        Return
          dict
        Modifed Attributes
          _markov
        """
        prev = None
        mars_list = dict()
        for each in data.split():
            each_pres = each # Preserve a copy
            
            # Check if word is start/end of sentence
            start = self.is_start(prev, each)
            end = self.is_end(each)

            each = Markov.sanitize_word(each).lower()

            if not each in mars_list:
                mars_list[each] = MarkovStruct(each)

            if prev:
                try:
                    mars = Markov.sanitize_word(prev).lower()
                    mars_list[mars].add_transitions(mars_list[each].token)
                except KeyError: # Ignore any unique or malformed words.
                    pass

            # If necessary, flip the flags.
            if start:
                mars_list[each].start = start

            if end:
                mars_list[each].end = end
            prev = each_pres

        self._markov = mars_list
        return self._markov

    def deserialize(self, fin: Path):
        """Deserialize the data so it can be read from disk.

        Parameters
          fin -- Path : Path to the file to write.
        Return
          None if success
          str if error
        """
        try:
            fl = open(str(fin), "rb")
            self._markov = pickle.load(fl)
            fl.close()
        except FileNotFoundError as e:
            return e.strerror
        except EOFError as e:
            return e.strerror
        return None
        
    def serialize(self, fout: Path):
        """Serialize data so it can be written to disk.

        Parameters
          fout -- Path : Path to read file from.
        Return
          None if success
          str if error
        """
        try:
            if not fout.exists():
                fout.touch(mode=0o666, exist_ok=True)

            fl = open(str(fout), "wb")
            pickle.dump(self._markov, fl)
            fl.close()
        except FileNotFoundError as e:
            return e.strerror
        return None
