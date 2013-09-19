#!/usr/bin/env python
# encoding: utf-8

import unittest

import json
import pdb

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

# 'readdata' config item
class ReadData_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.datasource_json = configJson["from"]

        self.type = self.datasource_json["type"] # "json" presumably
        self.source = self.datasource_json["source"] # "url" presumably
        self.url = self.datasource_json["url"]  # url of the data
        
        self.subConfigItem = ConfigItem.createConfigItem(configJson["do"]) # check if ["do"] exists first ___

# 'if' config item
class If_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.condition_json = configJson["if-condition"]
        self.operator = self.condition_json["operator"]
        self.field_name = self.condition_json["field-name"]
        self.field_value = self.condition_json["field-value"]
        
        self.then_json = configJson["then"]
        self.then_subConfigItem = ConfigItem.createConfigItem(self.then_json["do"])        

# 'send-email' config item
class SendEmail_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.params_json = configJson["email-parameters"]
        self.emailaddress = self.params_json["email-address"]
        self.emailbody = self.params_json["email-body"]
        self.max_frequency = self.params_json["max-frequency"]


class Config:

    # read in config file
    def __init__(self, configPath):
        with open (configPath) as ff:
            self.data = json.load(ff)

        # build config tree
        self.configTree = ConfigItem.createConfigItem(self.data["settings"]["do"])

# Test configuration file reading and processing
class TestFeed(unittest.TestCase):

    # read a config file - check if it worked
    def test_readconfig(self):
        cfg = Config("testdata/testconfig.json")
        # make sure it starts with "settings" level
        self.assertTrue(cfg.configTree != None)
        self.assertEqual(cfg.configTree.__class__.__name__, "ReadData_ConfigItem")
        self.assertEqual(cfg.configTree.url, "http://developer.mbta.com/lib/RTCR/RailLine_10.json")
        self.assertEqual(cfg.configTree.subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.field_name, "Trip")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.field_name, "Vehicle")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.then_subConfigItem.__class__.__name__, "SendEmail_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.then_subConfigItem.then_subConfigItem.emailaddress, "olive.swanbeck@verizon.net")


if __name__ == '__main__':
    unittest.main()
