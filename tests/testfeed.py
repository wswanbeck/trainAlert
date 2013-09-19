#!/usr/bin/env python
# encoding: utf-8

import unittest
import urllib2

class TestFeed(unittest.TestCase):

    def test_getFeed(self):
        feed = urllib2.urlopen("http://developer.mbta.com/lib/RTCR/RailLine_10.json").read()
        print feed


if __name__ == '__main__':
    unittest.main()
