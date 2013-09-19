#!/usr/bin/env python
# encoding: utf-8

import unittest

import json
import pdb

class Config:

    # read in config file
    def __init__(self, configPath):
        with open (configPath) as ff:
            self.data = json.load(ff)

# Test configuration file reading and processing
class TestFeed(unittest.TestCase):

    def test_readconfig(self):
        cfg = Config("testdata/testconfig.json")
        self.assertTrue(cfg.data["settings"] != None)

if __name__ == '__main__':
    unittest.main()
