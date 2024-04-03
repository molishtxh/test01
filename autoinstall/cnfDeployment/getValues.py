#!/usr/bin/python3
import os
import sys
import re
import getpass
import datetime
import collections
import yaml
import ipaddress

def ordered_yaml_load(yaml_path, Loader=yaml.Loader):
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return collections.OrderedDict(loader.construct_pairs(node))
    Loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    with open(yaml_path) as stream:
        return yaml.load(stream, Loader)

def ordered_yaml_dump(data, stream, Dumper=yaml.SafeDumper):
    def represent_dict(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, list(data.items()))
    def represent_none(self,_):
       return self.represent_scalar('tag:yaml.org,2002:null', '')
    def represent_anchor_wrapper(dumper, data):
       if isinstance(data[0], bool):
          return dumper.represent_bool(data[0])
       elif isinstance(data[0], int):
          return dumper.represent_int(data[0])
       elif isinstance(data[0], str):
          return dumper.represent_str(data[0])
       else:
          raise ValueError()
    Dumper.add_representer(collections.OrderedDict, represent_dict)
    Dumper.add_representer(type(None), represent_none)
    Dumper.add_representer(AnchorWrapper, represent_anchor_wrapper)
    yaml.dump(data,
              stream,
              Dumper,
              default_flow_style=False,
              encoding='utf-8',
              allow_unicode=True)
    stream.write("\n")

class AnchorWrapper(tuple):
  def __new__(cls, value):
    return tuple.__new__(cls, [value])

class ValuesDumper(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super(ValuesDumper, self).write_line_break(data)
        if len(self.indents) == 1:
            super(ValuesDumper, self).write_line_break()

def getAvliableIPSets():
    ip_sets = {}
    ip_plan = ordered_yaml_load("valuesYamlTemplate.yaml")
    for lan in ["ldapLan", "ldaplbLan", "vnflbLan", "diam1Lan", "triggerLan", "acreencryptLan", "http2lbLan", "liLan", "hsm1Lan", "hsm2Lan", "diam2Lan", "diammh1Lan", "diammh2Lan", "sigpLanhlr", "sigsLanhlr", "InterCE1Lanhlr", "InterCE2Lanhlr", "InterCE3Lanhlr"]:
        ip_sets[lan] = {}
        ip_sets[lan]["startIP"] = ip_plan[lan]["allocationPoolStartIp"]
        ip_sets[lan]["AvliableIP"] = ip_sets[lan]["startIP"]
        ip_sets[lan]["cidrlen"] = re.findall('(?<=\/).*$', ip_plan[lan]["cidr"])
    return ip_sets

def getNextAvliableIP(ip_sets, lan):
    result = ip_sets[lan]["AvliableIP"]
    ip_sets[lan]["AvliableIP"] = str(ipaddress.ip_address(str(result))+1)
    return result + "/"+ ip_sets[lan]["cidrlen"][0]

def getAvaliableNetSets():
    net_sets = {}
    net_plan = ordered_yaml_load(helm_values_fileName)
    for lan in ["ldapLan", "ldaplbLan", "vnflbLan", "diam1Lan", "triggerLan", "acreencryptLan", "http2lbLan", "liLan", "hsm1Lan", "hsm2Lan", "diam2Lan", "diammh1Lan", "diammh2Lan", "sigpLanhlr", "sigsLanhlr", "InterCE1Lanhlr", "InterCE2Lanhlr", "InterCE3Lanhlr"]:
        net_sets[lan] = {}
        net_sets[lan]["allocationPoolStartIp"] = net_plan[lan]["allocationPoolStartIp"]
        net_sets[lan]["allocationPoolEndIp"] = net_plan[lan]["allocationPoolEndIp"]
        net_sets[lan]["hostDevice"] = net_plan[lan]["hostDevice"]
        net_sets[lan]["cidr"] = net_plan[lan]["cidr"]
        net_sets[lan]["routes"] = net_plan[lan]["routes"]
    return net_sets

def HelmConfigure():
    print("step: get ips for values.yaml start")
    values = ordered_yaml_load(values_yaml)
    if use_resource == "false":
       values["global"]["useResources"] = False
    if tenant_enabled == "true":
        repos = "harbor-harbor-core.ncms.svc/" + tenant_name
        values["global"]["repository"] = repos
    values["global"]["environment"]["vnfid"] = vnf_name
    values["global"]["environment"]["ztsnamespace"] = zts_namespace
    values["lcm"]["lcmsettings"]["ztslcmpassword"] = zts1user_passwd
    values["lcm"]["lcmsettings"]["preProvisionJob"] = "disable"
    values["global"]["pvcStorageClass"] = storage_class
    ip_sets = getAvliableIPSets()
    for line in values["global"]["http2lb"]["connections"]:
        ip = getNextAvliableIP(ip_sets, "http2lbLan")
        line["http2lbLan"] = ip
    for line in values["dlb"]["connections"]:
        ip = getNextAvliableIP(ip_sets, "diam1Lan")
        line["diam1Lan"] = ip
        ip = getNextAvliableIP(ip_sets, "diam2Lan")
        line["diam2Lan"] = ip
    values["ss7"]["connections"][0]["interCE1prim"] = getNextAvliableIP(ip_sets, "InterCE1Lanhlr")
    values["ss7"]["connections"][1]["interCE1sec"] = values["ss7"]["connections"][0]["interCE1prim"]
    values["ss7"]["connections"][1]["interCE1prim"] = getNextAvliableIP(ip_sets, "InterCE1Lanhlr")
    values["ss7"]["connections"][0]["interCE1sec"] = values["ss7"]["connections"][1]["interCE1prim"]
    values["ss7"]["connections"][0]["interCE2prim"] = getNextAvliableIP(ip_sets, "InterCE2Lanhlr")
    values["ss7"]["connections"][1]["interCE2sec"] = values["ss7"]["connections"][0]["interCE2prim"]
    values["ss7"]["connections"][1]["interCE2prim"] = getNextAvliableIP(ip_sets, "InterCE2Lanhlr")
    values["ss7"]["connections"][0]["interCE2sec"] = values["ss7"]["connections"][1]["interCE2prim"]
    values["ss7"]["connections"][0]["interCE3prim"] = getNextAvliableIP(ip_sets, "InterCE3Lanhlr")
    values["ss7"]["connections"][1]["interCE3sec"] = values["ss7"]["connections"][0]["interCE3prim"]
    values["ss7"]["connections"][1]["interCE3prim"] = getNextAvliableIP(ip_sets, "InterCE3Lanhlr")
    values["ss7"]["connections"][0]["interCE3sec"] = values["ss7"]["connections"][1]["interCE3prim"]
    values["ss7"]["connections"][0]["sigplan"] = getNextAvliableIP(ip_sets, "sigpLanhlr")
    values["ss7"]["connections"][1]["sigplan"] = getNextAvliableIP(ip_sets, "sigpLanhlr")
    values["ss7"]["connections"][0]["sigslan"] = getNextAvliableIP(ip_sets, "sigsLanhlr")
    values["ss7"]["connections"][1]["sigslan"] = getNextAvliableIP(ip_sets, "sigsLanhlr")
    net_sets = getAvaliableNetSets()
    for lan in ["ldapLan", "ldaplbLan", "vnflbLan", "diam1Lan", "triggerLan", "acreencryptLan", "http2lbLan", "liLan", "hsm1Lan", "hsm2Lan", "diam2Lan", "diammh1Lan", "diammh2Lan", "sigpLanhlr", "sigsLanhlr", "InterCE1Lanhlr","InterCE2Lanhlr", "InterCE3Lanhlr"]:
        startIP = net_sets[lan]["allocationPoolStartIp"]
        values["net-helm-chart-4G"][lan]["allocationPoolStartIp"] = str(ipaddress.ip_address(str(startIP)))
        endIP = net_sets[lan]["allocationPoolEndIp"]
        values["net-helm-chart-4G"][lan]["allocationPoolEndIp"] = str(ipaddress.ip_address(str(endIP)))
        values["net-helm-chart-4G"][lan]["hostDevice"] = str(net_sets[lan]["hostDevice"])
        values["net-helm-chart-4G"][lan]["cidr"] = str(net_sets[lan]["cidr"])
        values["net-helm-chart-4G"][lan]["routes"] = net_sets[lan]["routes"]
    with open(values_yaml, "w") as values_yaml_file:
        ordered_yaml_dump(values, values_yaml_file, ValuesDumper)

    print("step: get ips for values.yaml end")
    print("############################################")

def getInput():
    global zts1user_passwd
    global zts_namespace
    global vnf_name
    global use_resource
    global values_yaml
    global storage_class
    global helm_values_fileName
    global tenant_name
    global tenant_enabled
    if len(sys.argv) > 2:
        for param in sys.argv:
            if "helm_values_fileName=" in param:
                helm_values_fileName = param.split("=")[1]
            if "zts1user_passwd=" in param:
                zts1user_passwd = param.split("=")[1]
            if "vnf_name=" in param:
                vnf_name = param.split("=")[1]
            if "zts_namespace" in param:
                zts_namespace = param.split("=")[1]
            if "use_resource" in param:
                use_resource = param.split("=")[1]
            if "value_path" in param:
                values_yaml = param.split("=")[1]
            if "storage_class" in param:
                storage_class = param.split("=")[1]
            if "tenant_name" in param:
                tenant_name = param.split("=")[1]
            if "tenant_enabled" in param:
                tenant_enabled = param.split("=")[1]
getInput()
HelmConfigure()

