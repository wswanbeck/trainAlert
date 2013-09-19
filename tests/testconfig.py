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

    # read a config file - check if it worked
    def test_readconfig(self):
        cfg = Config("testdata/testconfig.json")
        # make sure it starts with "settings" level
        self.assertTrue(cfg.data["settings"] != None)
        # next level should be "addwatch"
        settings = cfg.data["settings"]
        self.assertTrue(settings["addwatch"] != None)

if __name__ == '__main__':
    unittest.main()
