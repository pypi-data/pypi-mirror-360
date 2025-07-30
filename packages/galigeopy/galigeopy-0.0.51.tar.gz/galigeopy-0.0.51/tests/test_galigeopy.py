import unittest
import os
import sys

from galigeopy.galigeopy import check

class TestGaligeopy(unittest.TestCase):
    def test_check(self):
        self.assertTrue(check())
