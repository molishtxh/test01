#!/usr/bin/python3

import os
import sys
import re
import datetime
import time
from optparse import OptionParser
import yaml
import collections

scriptHome = "."
if os.path.dirname(sys.argv[0]) != "":
    scriptHome = os.path.dirname(sys.argv[0]) + "/"
scriptHome = scriptHome + "/"

def ordered_yaml_load(yaml_path, Loader=yaml.Loader):
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return collections.OrderedDict(loader.construct_pairs(node))
    Loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    with open(yaml_path) as stream:
        return yaml.load(stream, Loader)

def parseGlobalValues(values_yaml="sdl_values.yaml"):
    global configureMap
    if os.path.exists(values_yaml):
        dict_config = ordered_yaml_load(values_yaml)
        configureMap = dict_config["global"]
        return configureMap
    else:
        raise ValueError("no values.yaml for %s" % config_type)
