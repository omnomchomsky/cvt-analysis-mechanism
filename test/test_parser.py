import unittest
import logging
from source.parser import CoverityXMLParser


class TestCoverityXMLParser(unittest.TestCase):

    def setUp(self):
        self.candidate = CoverityXMLParser()

    def test_diff_keys(self):
        old = {'a': 1, 'b': 1}
        new = {'a': 1, 'b': 1}
        self.assertTrue(self.candidate.compare_keys(old, new))
        new = {'a': 1}
        self.assertTrue(self.candidate.compare_keys(old, new))
        new = {'a': 1, 'b': 1, 'c': 1}
        self.assertFalse(self.candidate.compare_keys(old, new))
        new = {'c': 1}
        self.assertFalse(self.candidate.compare_keys(old, new))

    def test_diff_values(self):
        old = {'a': 1, 'b': 1}
        new = {'a': 1, 'b': 1}
        self.assertTrue(self.candidate.compare_values(old, new))
        new = {'a': 0}
        self.assertTrue(self.candidate.compare_values(old, new))
        new = {'a': 2, 'b': 1, 'c': 1}
        self.assertFalse(self.candidate.compare_values(old, new))
        new = {'b': 2}
        self.assertFalse(self.candidate.compare_values(old, new))


if __name__ == '__main__':
    TestCoverityXMLParser.setUp()
