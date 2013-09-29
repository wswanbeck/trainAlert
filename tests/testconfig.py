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
        elif type == "schedule":
            ret = Schedule_ConfigItem(jsonData)
        else:
            print "**** Unknown element in config: '" + str(type) + "'"
            ret = None

        return ret

    def run(self, context, feeddata):
        print "running ConfigItem base class"

# 'schedule' config item
class Schedule_ConfigItem(ConfigItem):

    def __init__ (self, configJson):
        self.schedule_days = configJson["schedule-days"]
        self.complete_variable_name = configJson["complete-variable-name"]
        self.subConfigItem = ConfigItem.createConfigItem(configJson["do"]) # check if ["do"] exists first ___

    def run(self, context, feeddata):
        # check if alert has already been sent
        if self.complete_variable_name in context:
            if context[self.complete_variable_name]:
                return  # already done today, don't do it again
        else:
            context[self.complete_variable_name] = False

        self.subConfigItem.run(context, feeddata)

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

    def run(self, context, feeddata):
        # ignore incoming feeddata.  We set it to whatever we've been directed to read
        if self.source == "url":
            self.feeddata = urllib2.urlopen(self.url).read()
        elif self.source == "filepath":
            with open(self.filepath) as f:
                self.feeddata = f.read()
        # call this subitem repeatedly for each ["Message"] in the feeddata data we just read in
        for message in json.loads(self.feeddata)["Messages"]:
            self.subConfigItem.run(context, message)

# 'if' config item
class If_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.condition_json = configJson["if-condition"]
        self.operator = self.condition_json["operator"]
        self.field_name = self.condition_json["field-name"]
        self.field_value = self.condition_json["field-value"]
        
        self.then_json = configJson["then"]
        self.then_subConfigItem = ConfigItem.createConfigItem(self.then_json["do"])        

    def run(self, context, feeddata):
        if self.operator == "not-equal":
            if str(feeddata[self.field_name]) != str(self.field_value):
                self.then_subConfigItem.run(context, feeddata)
        elif self.operator == "equal":
            if str(feeddata[self.field_name]) == str(self.field_value):
                self.then_subConfigItem.run(context, feeddata)

# 'send-email' config item
class SendEmail_ConfigItem(ConfigItem):

    def __init__(self, configJson):
        self.params_json = configJson["email-parameters"]
        self.emailaddress = self.params_json["email-address"]
        self.emailbody = self.params_json["email-body"]
        self.set_variable = None
        if "set-variable" in self.params_json:
            self.set_variable = self.params_json["set-variable"]

    def run(self, context, feeddata):
        print "Message is: " + self.emailbody % feeddata
        # set the variable in the context that we were told to now that we've sent an alert
        pdb.set_trace()
        if self.set_variable != None:
            context[self.set_variable] = True

class Config:

    # read in config file
    def __init__(self, configPath):
        with open (configPath) as ff:
            self.data = json.load(ff)

        # build config tree
        self.configTree = ConfigItem.createConfigItem(self.data["settings"]["do"])

    def run(self):
        if self.configTree != None:
            self.configTree.run({}, "")
        else:
            print "**** Config not parsed.  Nothing will be run"

# Test configuration file reading and processing
class TestFeed(unittest.TestCase):

    # read a config file - check if it worked
    def test_readconfig(self):
        cfg = Config("testdata/testconfig.json")
        # make sure it starts with "settings" level
        self.assertTrue(cfg.configTree != None)
        self.assertEqual(cfg.configTree.__class__.__name__, "Schedule_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.__class__.__name__, "ReadData_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.filepath, "./testdata/testMBTAfeed.json")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.field_name, "Trip")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.then_subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.then_subConfigItem.field_name, "Vehicle")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.then_subConfigItem.__class__.__name__, "If_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.then_subConfigItem.then_subConfigItem.__class__.__name__, "SendEmail_ConfigItem")
        self.assertEqual(cfg.configTree.subConfigItem.subConfigItem.then_subConfigItem.then_subConfigItem.emailaddress, "olive.swanbeck@verizon.net")

    def test_runconfig(self):
        cfg = Config("testdata/testconfig.json")
        cfg.run()

    def test_runconfig_online(self):
        cfg = Config("testdata/testconfig_online.json")
        cfg.run()


if __name__ == '__main__':
    unittest.main()
