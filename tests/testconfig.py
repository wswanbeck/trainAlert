#!/usr/bin/env python
# encoding: utf-8

import unittest

import json
import pdb
import urllib2

# base class for all configuration items
class ConfigItem:
    
    @staticmethod
    def createConfigItem(jsonData):

        type = jsonData["type"]

        if type == "readdata":
            ret = ReadData_ConfigItem(jsonData)
        elif type == "if":
            ret = If_ConfigItem(jsonData)
        elif type == "send-email":
            ret = SendEmail_ConfigItem(jsonData)

        return ret

    def run(self, context):
        print "running ConfigItem base class"

# 'readdata' config item
class ReadData_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.datasource_json = configJson["from"]

        self.type = self.datasource_json["type"] # "json" presumably
        self.source = self.datasource_json["source"] # "url" or "filepath"
        if self.source == "url":
            self.url = self.datasource_json["url"]  # url of the data
        elif self.source == "filepath":
            self.filepath = self.datasource_json["filepath"]
        
        self.subConfigItem = ConfigItem.createConfigItem(configJson["do"]) # check if ["do"] exists first ___

    def run(self, context):
        print "running ReadData_ConfigItem class"
        # ignore incoming context.  We set it to whatever we've been directed to read
        if self.source == "url":
            self.context = urllib2.urlopen(self.url).read()
        elif self.source == "filepath":
            with open(self.filepath) as f:
                self.context = f.read()
        self.subConfigItem.run(self.context)

# 'if' config item
class If_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.condition_json = configJson["if-condition"]
        self.operator = self.condition_json["operator"]
        self.field_name = self.condition_json["field-name"]
        self.field_value = self.condition_json["field-value"]
        
        self.then_json = configJson["then"]
        self.then_subConfigItem = ConfigItem.createConfigItem(self.then_json["do"])        

    def run(self, context):
        print "running If_ConfigItem class"

# 'send-email' config item
class SendEmail_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.params_json = configJson["email-parameters"]
        self.emailaddress = self.params_json["email-address"]
        self.emailbody = self.params_json["email-body"]
        self.max_frequency = self.params_json["max-frequency"]

    def run(self, context):
        print "running SendEmail_ConfigItem"
        print "Message is: " + self.emailbody
        print "Context is: " + context


class Config:

    # read in config file
    def __init__(self, configPath):
        with open (configPath) as ff:
            self.data = json.load(ff)

        # build config tree
        self.configTree = ConfigItem.createConfigItem(self.data["settings"]["do"])

    def run(self):
        self.configTree.run("")

# Test configuration file reading and processing
class TestFeed(unittest.TestCase):

    # read a config file - check if it worked
    def test_readconfig(self):
        cfg = Config("testdata/testconfig.json")
        # make sure it starts with "settings" level
        self.assertTrue(cfg.configTree != None)
        self.assertEqual(cfg.configTree.__class__.__name__, "ReadData_ConfigItem")
        self.assertEqual(cfg.configTree.filepath, "./testdata/testMBTAfeed.json")
        self.assertEqual(cfg.configTree.subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.field_name, "Trip")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.field_name, "Vehicle")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.then_subConfigItem.__class__.__name__, "SendEmail_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.then_subConfigItem.emailaddress, "olive.swanbeck@verizon.net")

    def test_runconfig(self):
        cfg = Config("testdata/testconfig.json")
        cfg.run()

    def test_runconfig_online(self):
        cfg = Config("testdata/testconfig_online.json")
        cfg.run()


if __name__ == '__main__':
    unittest.main()
