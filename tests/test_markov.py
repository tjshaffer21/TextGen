#!/usr/bin/env python3

import unittest
from textgen import markov

class TestMarkovStruct(unittest.TestCase):
    def setUp(self):
        self.token = "A"
        self.markov = markov.MarkovStruct(self.token)

    def test_init(self):
        self.assertEqual(self.token, self.markov.token)
        self.assertEqual([], self.markov.transitions)

    def test_properties(self):
        self.assertEqual(False, self.markov.start, 'Wrong start')
        self.assertEqual([], self.markov.end, 'Wrong end')

        self.markov.start = True
        self.assertEqual(True, self.markov.start, 'Wrong start')

        self.markov.add_punctuation('.')
        self.assertEqual(['.'], self.markov.end, 'Wrong end')

    def test_transtions(self):
        self.markov.add_transitions(None)
        self.assertEqual([], self.markov.transitions, 'Invalid transitions')

        self.markov.add_transitions("B")
        self.assertEqual(["B"], self.markov.transitions, 'Invalid transitions')

        self.markov.add_transitions(["C", "D", "E"])
        self.assertEqual(["B", "C", "D", "E"], self.markov.transitions,
                         'Invalid transitions')


class TestMarkov(unittest.TestCase):
    def setUp(self):
        self.ms = markov.MarkovStruct("A")

    def test_is_start(self):
        prev = "Hello"
        prevp = "Hello!"
        check = "Sir"

        self.assertEqual(True, markov.Markov.is_start(None, check),
                         'Invalid start')
        self.assertEqual(False, markov.Markov.is_start(prev, check),
                         'Invalid start')
        self.assertEqual(True, markov.Markov.is_start(prevp, check),
                         'Invalid start')

    def test_is_end(self):
        e1 = "Hello"
        e2 = "tomorrow."
        e3 = "terror,"

        self.assertEqual(False, markov.Markov.is_end(e1), 'Invalid end')
        self.assertEqual(True, markov.Markov.is_end(e2), 'Invalid end')
        self.assertEqual(False, markov.Markov.is_end(e3), 'Invalid end')

    def test_train(self):
        mock = "It goes without saying. 'twas a long night!"

        m1 = markov.MarkovStruct("it", ["goes"])
        m1.start = True

        m2 = markov.MarkovStruct("goes", ["without"])

        m3 = markov.MarkovStruct("without", ["saying"])

        m4 = markov.MarkovStruct("saying", ["twas"])
        m4.add_punctuation('.')

        m5 = markov.MarkovStruct("twas", ["a"])
        m5.start = True

        m6 = markov.MarkovStruct("a", ["long"])
        m7 = markov.MarkovStruct("long", ["night"])

        m8 = markov.MarkovStruct("night")
        m8.add_punctuation('!')

        mock_res = { 'it' : m1, 'goes' : m2, 'without' : m3, 'saying' : m4,
                     'twas' : m5, 'a' : m6, 'long' : m7, 'night' : m8}
        mark = markov.Markov()
        mark.train(mock)

        self.maxDiff = None
        self.assertDictEqual(mock_res, mark._markov, 'Invalid training')

    def test_strip_front(self):
        w1 = "apple"
        self.assertEqual("apple", markov.Markov.strip_front(w1), 'Failure')
        w2 = "!apple"
        self.assertEqual("apple", markov.Markov.strip_front(w2), 'Failure')
        w4 = "'you"
        self.assertEqual("you", markov.Markov.strip_front(w4), 'Failure')
        w5 = "'Sparrow"
        self.assertEqual("Sparrow", markov.Markov.strip_front(w5), 'Failure')
        w7 = "--hassle"
        self.assertEqual("hassle", markov.Markov.strip_front(w7), 'Failure')

    def test_strip_back(self):
        w1 = "apple"
        self.assertEqual("apple", markov.Markov.strip_back(w1), 'Failure')
        w3 = "apple!"
        self.assertEqual("apple", markov.Markov.strip_back(w3), 'Failure')
        w4 = "apple!!!!"
        self.assertEqual("apple", markov.Markov.strip_back(w4), 'Failure')
        w5 = "apple-!."
        self.assertEqual("apple", markov.Markov.strip_back(w5), 'Failure')
        
        self.assertEqual("apple", markov.Markov.strip_back(w5, ['!']),
                         'Failure')
        self.assertEqual("apple!", markov.Markov.strip_back(w5, ['!'], 1),
                         'Failure')
        self.assertEqual("apple!", markov.Markov.strip_back(w5, ['!'], 2),
                         'Failure')
        self.assertEqual("apple!!", markov.Markov.strip_back(w4, ['!'], 2),
                         'Failure')
                                                                
        
if __name__ == '__main__':
    unittest.main()
