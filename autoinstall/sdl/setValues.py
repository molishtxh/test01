#!/usr/bin/python3
import os
import sys
import re
import getpass
import datetime
import collections
import yaml
import ipaddress
import copy

sdl_global = "sdl_global.cfg"
pgw_global = "pgw_global.cfg"
sdl_global_yaml = "sdl_global.yaml"
pgw_global_yaml = "pgw_global.yaml"
config_type = "sdl"
vip_path_postfix = "MISC/charts-values-examples/vip-crd/"
pgw_vip_path_postfix = "MISC/charts-values-examples/vip-crd/scenario2/"
sdl_yaml = "sdl_values_ok.yaml"
pgw_yaml = "pgw_values_ok.yaml"

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

def sdlpreConfigGlobalValues(global_file, global_file_tmp, dict, dict_global):
    print("step: preconfig sdl global data, generating global values yaml")
    for key in dict_global.keys():
        component = key.split("/")[1]
        if "sdl_repository_prefix" in dict.keys():
            if component in dict_global[key].keys():
                if dict["sdl_repository_prefix"].endswith("/"):
                    new_repository = dict["sdl_repository_prefix"] + component
                else:
                    new_repository = dict["sdl_repository_prefix"] + "/" + component
                if "image" in dict_global[key][component].keys():
                    if "repository" in dict_global[key][component]["image"].keys():
                        dict_global[key][component]["image"]["repository"] = new_repository
        if "sdl_sanfqdn1" in dict.keys() or "sdl_sanfqdn2" in dict.keys():
            if component in dict_global[key].keys():
                if "sdlsec" in dict_global[key][component].keys():
                    if "service" in dict_global[key][component]["sdlsec"]:
                        if "zts_ca" in dict_global[key][component]["sdlsec"]["service"]:
                            if "sanfqdn1" in dict_global[key][component]["sdlsec"]["service"]["zts_ca"]:
                                dict_global[key][component]["sdlsec"]["service"]["zts_ca"]["sanfqdn1"] = component + "-" + dict["sdl_sanfqdn1"]
                            if "sanfqdn2" in dict_global[key][component]["sdlsec"]["service"]["zts_ca"]:
                                dict_global[key][component]["sdlsec"]["service"]["zts_ca"]["sanfqdn2"] = component + "-" + dict["sdl_sanfqdn2"]
        if "ztslfs_tag" in dict.keys():
            if "ztslfs" in dict_global[key].keys():
                if "image" in dict_global[key]["ztslfs"].keys():
                    if "tag" in dict_global[key]["ztslfs"]["image"].keys():
                        dict_global[key]["ztslfs"]["image"]["tag"] = dict["ztslfs_tag"]
    with open(global_file_tmp, "w") as values_yaml_file:
        ordered_yaml_dump(dict_global, values_yaml_file, ValuesDumper)


def pgwpreConfigGlobalValues(global_file, global_file_tmp, dict, dict_global):
    print("step: pre config pgw global data")
    print("############################################")
    for key in dict_global.keys():
        component = key.split("/")[1]
        if "repository" in dict.keys():
            if component in dict_global[key].keys():
                new_repository = dict["repository"] + "/" + component
                if "image" in dict_global[key][component].keys():
                    if "repository" in dict_global[key][component]["image"].keys():
                        dict_global[key][component]["image"]["repository"] = new_repository
    with open(global_file_tmp, "w") as values_yaml_file:
        ordered_yaml_dump(dict_global, values_yaml_file, ValuesDumper)

def generateGlobalValues(global_file, global_file_tmp, dict):
    print("step: generate sdl/pgw global data")
    dict_yaml = ordered_yaml_load(global_file)
    if "sdl" == config_type:
        sdlpreConfigGlobalValues(global_file, global_file_tmp, dict, dict_yaml)
        configCommonGlobal(global_file_tmp, sdl_global_yaml, dict)
    else:
        pgwpreConfigGlobalValues(global_file, global_file_tmp, dict, dict_yaml)
        configCommonGlobal(global_file_tmp, pgw_global_yaml, dict)

def get_dict_values(in_dict, target_key, results=[], not_d=True):
    for key in in_dict.keys():
        data = in_dict[key]
        if isinstance(data, dict):
            get_dict_values(data, target_key, results=results, not_d=not_d)
        if key == target_key and isinstance(data, dict) != not_d:
            results.append(in_dict[key])
    return results

def configCommonGlobal(global_file, global_file_tmp, dict):
    file1 = open(global_file, 'r+')
    file2 = open(global_file_tmp, 'w+')
    for ss in file1.readlines():
        if ss.strip() != "":
            key_value = ss.strip().rstrip(":")
            for global_value in dict.keys():
                if global_value.startswith(config_type) and global_value.endswith(key_value):
                    new_ss = ss.rstrip() + " " +  str(dict[global_value]) + "\n"
                    file2.write(new_ss)
                    break
            else:
                file2.write(ss)
        else:
            file2.write(ss)


def setValuesYaml(config_yaml):
    for values in config_yaml.keys():
        if "global" != values:
            if ".yaml" not in values:
                values_name = values_path + "CHARTS/"+ values + "/values.yaml"
            else:
                values_name = values_path + values
            values_yaml_ofc = values_name.split(".yaml")[0] + "_ofc.yaml"
            if not os.path.exists(values_yaml_ofc):
                os.system("cp " + values_name + " " + values_yaml_ofc)
            template_values = ordered_yaml_load(values_name)
            result = merge_data(template_values, config_yaml[values])
            print("merging config data to %s" % values_name)
            with open(values_name, "w") as values_yaml_file:
                ordered_yaml_dump(result, values_yaml_file, ValuesDumper)

def generateValuesYaml():
    values_yaml = ordered_yaml_load(helm_values_fileName)
    for values in values_yaml.keys():
        if "global" == values:
            global_file = helm_values_fileName[0:3] +"_global.cfg"
            global_temp = global_file[:-4] + "_tmp.yaml"
            generateGlobalValues(global_file, global_temp, values_yaml[values])
            if "sdl" == config_type:
                global_yaml = sdl_global_yaml
            else:
                global_yaml = pgw_global_yaml
                generateNetwork(values_yaml)
            global_values_yaml = ordered_yaml_load(global_yaml)
            setValuesYaml(global_values_yaml)
        else:
            if "sdl" == config_type and "infracommon" == values:
                generateNetwork(values_yaml)
                if os.path.exists(sdl_yaml):
                    values_yaml = ordered_yaml_load(sdl_yaml)
            setValuesYaml(values_yaml)


def generateVipLan(values_yaml, primaryInterface, virtualRouterID, vip_lan):
    print("step: generate sdl/pgw vip-crd IP for %s" % vip_lan)
    vip_ofc = vip_lan.split(".yaml")[0] + "_ofc.yaml"
    os.system("cp " + vip_lan + " " + vip_ofc)
    file1 = open(vip_ofc, 'r+')
    file2 = open(vip_lan, 'w+')
    if "sdl" == config_type:
        vip_end = values_yaml['ipv4']['subnets']['allocation_pool']['end']
    else:
        ipaddress = values_yaml['ipv4']['subnets']['address']
    vip_subnet = values_yaml['ipv4']['subnets']['subnet'].split('/')[-1]
    vip_interface = values_yaml['host_device']
    vip_cidr = values_yaml['ipv4']['subnets']['routes'][0]['destination']
    vip_gateway = values_yaml['ipv4']['subnets']['routes'][0]['gateway']
    for ss in file1.readlines():
        new_ss = ss
        if "primaryInterface:" in ss:
            new_ss = ss.split(":")[0] + ": " + primaryInterface + "\n"
        elif "virtualRouterID:" in ss:
            new_ss = ss.split(":")[0] + ": " + str(virtualRouterID) +"\n"
            virtualRouterID = virtualRouterID +1
        elif "address:" in ss:
            if "sdl" == config_type:
                new_ss = ss.split(":")[0] + ": " + vip_end + "/" + vip_subnet + "\n"
            else:
                new_ss = ss.split(":")[0] + ": " + ipaddress + "/" + vip_subnet + "\n"
        if "interface" in ss:
            new_ss = ss.split(":")[0] + ": " + vip_interface + "\n"
        elif "cidr:" in ss:
            new_ss = ss.split(":")[0] + ": " + vip_cidr + "\n"
        if "via:" in ss:
            new_ss = ss.split(":")[0] + ": " + vip_gateway + "\n"
        file2.write(new_ss)
    file1.close()
    file2.close()


def generateCommonData():
    print("step: config sdl IP and common data")
    values_yaml = ordered_yaml_load(helm_values_fileName)
    oam_cidr = values_yaml['infracommon']['networks']['ext_oam_network']['ipv4']['subnets']['subnet'].split('/')[-1]
    app_cidr = values_yaml['infracommon']['networks']['ext_app_network']['ipv4']['subnets']['subnet'].split('/')[-1]
    intdb_cidr = values_yaml['infracommon']['networks']['int_db_network']['ipv4']['subnets']['subnet'].split('/')[-1]
    extdb_cidr = values_yaml['infracommon']['networks']['ext_db_network']['ipv4']['subnets']['subnet'].split('/')[-1]
    oam_start = values_yaml['infracommon']['networks']['ext_oam_network']['ipv4']['subnets']['allocation_pool']['start']
    app_start = values_yaml['infracommon']['networks']['ext_app_network']['ipv4']['subnets']['allocation_pool']['start']
    intdb_start = values_yaml['infracommon']['networks']['int_db_network']['ipv4']['subnets']['allocation_pool']['start']
    extdb_start = values_yaml['infracommon']['networks']['ext_db_network']['ipv4']['subnets']['allocation_pool']['start']
    oam_end = values_yaml['infracommon']['networks']['ext_oam_network']['ipv4']['subnets']['allocation_pool']['end']
    app_end = values_yaml['infracommon']['networks']['ext_app_network']['ipv4']['subnets']['allocation_pool']['end']
    intdb_end = values_yaml['infracommon']['networks']['int_db_network']['ipv4']['subnets']['allocation_pool']['end']
    extdb_end = values_yaml['infracommon']['networks']['ext_db_network']['ipv4']['subnets']['allocation_pool']['end']
    values_yaml['infracommon']['common']['extapplandbaccess0'] = str(app_start) + "/" + app_cidr
    values_yaml['infracommon']['common']['extapplandbaccess1'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(app_start)) + 1)) + "/" + app_cidr
    values_yaml['infracommon']['common']['fqdn_extapplandbaccess0'] = 'nc2748vip2_041.tre.nsn-rdnet.net'
    values_yaml['infracommon']['common']['fqdn_extapplandbaccess1'] = 'nc2748vip2_042.tre.nsn-rdnet.net'

    values_yaml['infracommon']['common']['intdblandbaccess0'] = str(intdb_start) + "/" + intdb_cidr
    values_yaml['infracommon']['common']['intdblandbaccess1'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(intdb_start)) + 1)) + "/" + intdb_cidr
    values_yaml['infracommon']['common']['extdblandbaccess0'] = str(extdb_start) + "/" + extdb_cidr
    values_yaml['infracommon']['common']['extdblandbaccess1'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(extdb_start)) + 1)) + "/" + extdb_cidr
    values_yaml['infracommon']['common']['fqdn_extdblandbaccess0'] = 'nc2748vip1_001.tre.nsn-rdnet.net'
    values_yaml['infracommon']['common']['fqdn_extdblandbaccess1'] = 'nc2748vip1_002.tre.nsn-rdnet.net'

    values_yaml['infracommon']['common']['intdblandbstorage0'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(intdb_start)) + 2)) + "/" + intdb_cidr
    values_yaml['infracommon']['common']['intdblandbstorage1'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(intdb_start)) + 3)) + "/" + intdb_cidr
    values_yaml['infracommon']['common']['extdblandbstorage0'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(extdb_start)) + 2)) + "/" + extdb_cidr
    values_yaml['infracommon']['common']['extdblandbstorage1'] = str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(extdb_start)) + 3)) + "/" + extdb_cidr
    values_yaml['infracommon']['common']['fqdn_extdblandbstorage0'] = 'nc2748vip1_003.tre.nsn-rdnet.net'
    values_yaml['infracommon']['common']['fqdn_extdblandbstorage1'] = 'nc2748vip1_004.tre.nsn-rdnet.net'

    dict_global = ordered_yaml_load(helm_values_fileName[0:3] +"_global.cfg")
    for key in dict_global.keys():
        if "infracommon" in key:
            dict_global[key]['common']['ingress']['cas']['ext_app_ipv4_ips'][0] = app_end
            dict_global[key]['common']['ingress']['cas']['ext_oam_ipv4_ips'][0] = oam_end
            dict_global[key]['common']['ingress']['oes']['ext_oam_ipv4_ips'][0] = oam_end
            dict_global[key]['common']['ingress']['ntf_kafka']['ext_app_ipv4_ips'][0] = app_end
            dict_global[key]['common']['ingress']['ntf_kafka']['ext_app_ipv4_ips'][1] = app_end
            dict_global[key]['common']['ingress']['ntf_kafka']['ext_app_ipv4_ips'][2] = app_end
            dict_global[key]['common']['ingress']['ntf_kafka']['ext_db_ipv4_ips'][0] = extdb_end
            dict_global[key]['common']['ingress']['diag']['ext_oam_ipv4_ips'][0] = oam_end
            dict_global[key]['common']['ingress']['ntf']['ext_app_ipv4_ips'][0] = app_end
            dict_global[key]['common']['ingress']['ntf']['ext_app_ipv4_port'][0] = '21805'
            dict_global[key]['common']['ingress']['disco']['ext_app_ipv4_ips'][0] = app_end
            dict_global[key]['common']['ingress']['disco']['ext_app_ipv4_port'][0] = '21805'

            dict_global[key]['common']['egress']['ext_oam'][0] = oam_end
            dict_global[key]['common']['egress']['ext_app'][0] = app_end
            dict_global[key]['common']['egress']['ext_db'][0] = extdb_end

            dict_global[key]['common']['kafkasslcert_password'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['opsuser'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['discouser'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['cmuser'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['rls'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['vnfm'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['oes'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['pgwadminuser'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['pgwoperdefault'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['pgwlidefault'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['notrgopdefault'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['notifsconfig'] = values_yaml['global']['user_password_base64']
            dict_global[key]['common']['users']['expmanager'] = values_yaml['global']['user_password_base64']
            values_yaml['infracommon']['common']['ingress'] = dict_global[key]['common']['ingress']
            values_yaml['infracommon']['common']['egress'] = dict_global[key]['common']['egress']
            values_yaml['infracommon']['common']['kafkasslcert_password'] = dict_global[key]['common']['kafkasslcert_password']
            values_yaml['infracommon']['common']['users'] = dict_global[key]['common']['users']

    values_yaml['infracommon']['common']['zts_ca_endpoints']['zts1']['ip'] = values_yaml['global']['zts_envoy_ip1'] + "," + values_yaml['global']['zts_envoy_ip2']
    values_yaml['dbaccess'] = {}
    values_yaml['dbaccess']['global'] = {}
    values_yaml['dbaccess']['global']['ztsentrypoint'] = values_yaml['global']['zts_envoy_ip1']
    values_yaml['dbaccess']['global']['ztsnamespace'] = values_yaml['global']['zts_ns']
    values_yaml['clustermonitoragent']['global']['ZTSLB1IP'] = values_yaml['global']['zts_envoy_ip1']
    values_yaml['clustermonitoragent']['global']['ZTSLB2IP'] = values_yaml['global']['zts_envoy_ip2']

    with open(sdl_yaml, "w") as values_yaml_file:
        ordered_yaml_dump(values_yaml, values_yaml_file, ValuesDumper)

def generateNetwork(values_yaml):
    if "sdl" == config_type and "infracommon" in values_yaml.keys() and "networks" in values_yaml["infracommon"].keys():
        vip_path = values_path + vip_path_postfix
        virtualRouterID = 134
        for key in values_yaml["infracommon"]["networks"].keys():
            vip_lan = vip_path + key.split("_")[1] + "-" + "vip.yaml"
            if "int_db_network" != key:
                primaryInterface = values_yaml["infracommon"]["networks"]["ext_oam_network"]["host_device"]
                generateVipLan(values_yaml["infracommon"]["networks"][key], primaryInterface, virtualRouterID, vip_lan)
                virtualRouterID = virtualRouterID + 1
        generateCommonData()
    elif "pgw" == config_type:
        vip_path = values_path + pgw_vip_path_postfix
        virtualRouterID = 151
        for key in values_yaml["global"]["networks"].keys():
            vip_lan = vip_path + key.split("_")[0] + "-" + "vip.yaml"
            primaryInterface = values_yaml["global"]["primaryInterface"]
            generateVipLan(values_yaml["global"]["networks"][key], primaryInterface, virtualRouterID, vip_lan)
            virtualRouterID = virtualRouterID + 1
    else:
        raise ValueError("no network configure") 

def merge_data(data_1, data_2):
    if isinstance(data_1, dict) and isinstance(data_2, dict):
        new_dict = {}
        new_dict = collections.OrderedDict()
        d2_keys = list(data_2.keys())
        for d1k in data_1.keys():
            if d1k in d2_keys:    # d1, d2 have, go deeper level
                d2_keys.remove(d1k)
                new_dict[d1k] = merge_data(data_1.get(d1k), data_2.get(d1k))
            else:
                new_dict[d1k] = data_1.get(d1k) # d1 have, d2 no key
        for d2k in d2_keys: #d2 have, d1 no
            new_dict[d2k] = data_2.get(d2k)
        return new_dict
    else:
        if data_2 == None: #d2 no, d1 have
            return data_1
        else:          # d2 have
            return data_2


def getInput():
    global values_yaml
    global values_path
    global helm_values_fileName
    global config_type
    if len(sys.argv) > 2:
        for param in sys.argv:
            if "helm_values_fileName=" in param:
                helm_values_fileName = param.split("=")[1]
                if helm_values_fileName.startswith("sdl"):
                    config_type = "sdl"
                elif helm_values_fileName.startswith("pgw"):
                    config_type = "pgw"
                else:
                    raise ValueError("not a correct lab type")
            if "value_path" in param:
                values_path = param.split("=")[1]
getInput()
generateValuesYaml()
