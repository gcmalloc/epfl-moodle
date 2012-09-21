#!/usr/bin/env python2

from moodle import Moodle
import unittest

class TestMoodle(unittest.TestCase):
    def test_connection(self):
        moodle = Moodle(USERNAME, PASSWORD)
        self.assertTrue(moodle.is_connected())
