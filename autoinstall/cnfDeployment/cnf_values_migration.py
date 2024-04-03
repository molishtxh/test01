import os
import typing
import argparse
import copy
import yaml


ACCEPT_RELEASES = ["22.0", "22.2"]
"""ACCEPT_RELEASES maintain all the supported releases of HSS CNF, it should be updated with the product"""
TARGET_APS = ""
"""TARGET_APS is the target release APS number, it will auto get from the target template file"""


def _migrate_22_2(source_dict: dict) -> dict:
    """
    Migrate the values object from 22.0 to 22.2

    :return: target values object of 22.2
    """
    _target_dict = copy.deepcopy(source_dict)
    _target_aps = TARGET_APS if TARGET_APS else "IMSDL2221234"
    _vnf_id = _target_dict["global"]["environment"]["vnfid"]
    _zts_namespace = _target_dict["global"]["environment"]["ztsnamespace"]
    _registry = _target_dict["global"]["repository"]
    if _target_dict["global"].get("useResources", None) is not None:
        del _target_dict["global"]["useResources"]
    if _target_dict["global"]["featureflag"].get("podDisruptionBudgetEnabled", None) is not None:
        del _target_dict["global"]["featureflag"]["podDisruptionBudgetEnabled"]

    _target_dict["global"]["image"]["udmenvoy"]["tag"] \
        = _target_dict["global"]["image"]["admin"]["tag"] \
        = _target_dict["global"]["image"]["mcc"]["tag"] \
        = _target_dict["global"]["image"]["fbit"]["tag"] \
        = _target_dict["global"]["image"]["exporter"]["tag"] \
        = _target_dict["global"]["image"]["awsipmgmt"]["tag"] = _target_aps
    _target_dict["global"]["image"]["cnsbasidecar"]["tag"] = "22.0.135"
    _pod_infos = [
        {"pod": "arpf", "images": ["arpf"], "nodeSelector": "is_edge"},
        {"pod": "dlb", "images": ["dlb"], "nodeSelector": "is_edge"},
        {"pod": "http2lb", "images": ["http2lb", "http2lbmgmt"], "nodeSelector": "is_edge"},
        {"pod": "ldapdisp", "images": ["ldapdispMgnt"], "nodeSelector": "is_edge"},
        {"pod": "hsscallp", "images": ["hsscallp"], "nodeSelector": "is_worker"},
        {"pod": "hssli", "images": ["hssli"], "nodeSelector": "is_edge"},
        {"pod": "trigger", "images": ["trigger"], "nodeSelector": "is_edge"},
        {"pod": "ss7", "images": ["ss7"], "nodeSelector": "is_edge"},
        {"pod": "hlrcallp", "images": ["hlrcallp"], "nodeSelector": "is_worker"},
        {"pod": "lcm", "images": ["lcmhook"], "nodeSelector": "is_edge"},
        {"pod": "vnfclusterenvoylb", "images": [], "nodeSelector": "is_edge"},
        {"pod": "hssfla", "images": ["hssfla"], "nodeSelector": "is_worker"},
        {"pod": "clustermonitoragent", "images": ["ztsclustermonitoragent", "healthcheck"],
         "nodeSelector": "is_worker"},
        {"pod": "dco", "images": ["dco"], "nodeSelector": "is_worker"},
        {"pod": "hssxds", "images": ["hssxds"], "nodeSelector": "is_worker"}
    ]
    for item in _pod_infos:
        for image in item["images"]:
            if image in _target_dict[item["pod"]]["image"]:
                _target_dict[item["pod"]]["image"][image]["tag"] = _target_aps
            else:
                _target_dict[item["pod"]]["image"][image] = {"tag": _target_aps}
        _target_dict[item["pod"]]["nodeSelector"] = [{"key": item["nodeSelector"], "value": "true"}]
        _target_dict[item["pod"]]["tolerations"] = [
            {"effect": "NoExecute", "key": item["nodeSelector"], "operator": "Equal", "value": "true"}]
        _target_dict[item["pod"]]["serviceAccountName"] = ""
        _target_dict[item["pod"]]["podDisruptionBudgetEnabled"] = True
        if "lcm" != item["pod"]:
            _target_dict[item["pod"]]["podDisruptionBudgetEnabled"] = True
            _target_dict[item["pod"]]["podDisruptionBudget"] = "25%"

    _target_dict["global"]["timezoneHostMount"] = True
    _target_dict["global"]["enableInterPodTLSCom"] = False
    _target_dict["global"]["enableSysPtraceCap"] = True
    _target_dict["global"]["environment"]["relvervalue"] = "22.2.0"
    _target_dict["global"]["healthCheck"] = {"cnfHealthCheckEnabled": False, "cpuThreshHold": 80, "memThreshHold": 90}
    _target_dict["global"]["cnsba"] = {"enabled": False,
                                       "crdbHost": "true",
                                       "crdbSecret": "{}-crdb-redisio-creds-default".format(_vnf_id)}
    _target_dict["global"]["dlb"]["enableTlsOnInternalHd"] = False
    _target_dict["global"]["clusterResources"]["psp"] = {"define": True}
    _target_dict["global"]["etcd"] = {"enabled": True}
    _target_dict["global"]["cnsbaController"] = {"enabled": False}
    _target_dict["global"]["crdbRedisio"] = {"enabled": False}

    _target_dict["lcm"]["lcmsettings"]["certs"].append({"enabled": False, "application": "HLRCALLP.Diameter"})
    # todo check how to handle this ztstrackersettings
    _target_dict["clustermonitoragent"]["ztstrackersettings"] = {"ztstrackeruser": "", "ztstrackerpassword": ""}
    _target_dict["dco"]["serviceAccountNameForJob"] = ""
    _target_dict["hssxds"]["replicaCount"] = 2
    _target_dict["etcd"] = {}
    _target_dict["etcd"]["nodeSelector"] = [{"key": "is_worker", "value": "true"}]
    _target_dict["etcd"]["tolerations"] = [
        {"effect": "NoExecute", "key": "is_worker", "operator": "Equal", "value": "true"}]
    _target_dict["etcd"]["global"] = {"serviceAccountName": ""}
    _target_dict["etcd"]["service"] = {"PDB": {"enable": True, "maxUnavailable": "30%"}}
    _target_dict["cnsba-controller"] = {}
    _registry = _target_dict["global"]["repository"]
    _target_dict["cnsba-controller"]["global"] = {"registry": _registry}
    _target_dict["cnsba-controller"]["cnsba"] = {
        "enabled": False,
        "crdbHost": "true",
        "crdbSecret": "{}-crdb-redisio-creds-default".format(_vnf_id)}
    _target_dict["cnsba-controller"]["fullnameOverride"] = "{}-cnsba-controller".format(_vnf_id)
    _target_dict["cnsba-controller"]["egressLbEndpoint"] = "{}-http2lb-svc-egress:10001".format(_vnf_id)
    _target_dict["cnsba-controller"]["egressLbEndpointHttps"] = "{}-http2lb-svc-egress:10001".format(_vnf_id)
    _target_dict["cnsba-controller"]["serviceAccount"] = ""
    _target_dict["cnsba-controller"]["cnsba_oam"] = {"fullnameOverride": "{}-cnsba-oam".format(_vnf_id)}
    _target_dict["cnsba-controller"]["cnsbaSidecar"] = {
        "config": {"csd": {"dbHostName": "{}-crdb-redisio".format(_vnf_id)}}}
    _target_dict["cnsba-controller"]["cnsbaConfiguration"] = {
        "config": {"csd": {"dbHostName": "{}-crdb-redisio".format(_vnf_id)}}}
    _target_dict["cnsba-controller"]["controllerService"] = {
        "config": {"csd": {"dbHostName": "{}-crdb-redisio".format(_vnf_id)}}}
    _target_dict["cnsba-controller"]["k8sServiceDiscovery"] = {"namespaces": _zts_namespace}
    _target_dict["cnsba-controller"]["zts"] = {
        "majorRel": "22",
        "minorRel": "2.0",
        "vnfName": _vnf_id,
        "ztslIP": "ztslenvoylbservice.{}.svc.cluster.local".format(_zts_namespace),
        "caServiceFQDN": "caserverservice.{}.svc.cluster.local".format(_zts_namespace),
        "ztsSecretKeyRefName": "{}casecret".format(_vnf_id)
    }
    _target_dict["cnsba-controller"]["sidecar"] = {
        "env": {"targetIP": "ztslenvoylbservice.{}.svc.cluster.local".format(_zts_namespace)},
        "image": {"registry": _registry}
    }
    _target_dict["cnsba-controller"]["cnsbaMetrics"] = {"registry": _registry}

    _target_dict["crdb-redisio"] = {
        "fullnameOverride": "{}-crdb-redisio".format(_vnf_id),
        "serviceAccountName": "",
        "global": {"registry": _registry, "registry1": _registry, "registry2": _registry},
        "tls": {"enabled": False},
        "nodeAntiAffinity": "soft",
        "disableIPv6": True,
        "rbac": {"enabled": True}
    }
    return _target_dict


def _validation(source, target, values_path, template_path):
    global ACCEPT_RELEASES
    if source not in ACCEPT_RELEASES:
        raise ValueError("source release {} is not in the supported list".format(source))
    if target not in ACCEPT_RELEASES:
        raise ValueError("target release {} is not in the supported list".format(target))
    if ACCEPT_RELEASES.index(source) >= ACCEPT_RELEASES.index(target):
        raise ValueError("source release should lower than target release")
    with open(values_path, "r", encoding="utf-8") as _contents:
        _values_object = yaml.full_load(_contents)
        del _contents
        del _values_object
    with open(template_path, "r", encoding="utf-8") as _contents:
        _values_object = yaml.full_load(_contents)
        del _contents
        del _values_object


def migrate(source: str, target: str,
            values_path: typing.Union[str, bytes, os.PathLike],
            template_path: typing.Union[str, bytes, os.PathLike]) -> dict:
    """Migrate values of YAML file from source release to target release.

    :param source: the source release of the values, e.g. 22.0
    :param target: the source release e.g. 22.2
    :param values_path: the values of YAML file e.g. /home/test/value.yaml
    :param template_path: the target release values template

    :return target values object
    """
    _validation(source, target, values_path, template_path)
    with open(values_path, "r", encoding="utf-8") as _source_contents:
        _source_values_object = yaml.full_load(_source_contents)

    with open(template_path, "r", encoding="utf-8") as _target_contents:
        _target_values_object = yaml.full_load(_target_contents)
        del _target_contents

    global ACCEPT_RELEASES, TARGET_APS
    _start_index = ACCEPT_RELEASES.index(source) + 1
    _end_index = ACCEPT_RELEASES.index(target)
    TARGET_APS = _target_values_object["global"]["image"]["mcc"]["tag"]
    for index in range(_start_index, _end_index+1):
        fun_name = "_migrate_{}".format(ACCEPT_RELEASES[index]).replace(".", "_")
        _source_values_object = eval(fun_name)(_source_values_object)
    return _source_values_object


def dump(source: dict, values_path: typing.Union[str, bytes, os.PathLike]):
    with open(values_path, "w", encoding="utf-8") as _target_file:
        yaml.dump(source, _target_file, Dumper=yaml.SafeDumper)


def _parse_args():
    parser = argparse.ArgumentParser(description="A tool for HSS CNF values.yaml migration")
    parser.add_argument("-s", "--source", help="source release", choices=ACCEPT_RELEASES[:-1], required=True)
    parser.add_argument("-f", "--values", help="the existing release values YAML file", required=True)
    parser.add_argument("-t", "--target", help="the target release", choices=ACCEPT_RELEASES[1:],
                        default=ACCEPT_RELEASES[-1])
    parser.add_argument("-m", "--template", help="the target release values YAML file template", required=True)
    parser.add_argument("-o", "--output", help="the output YAML file",
                        default="Values_{}.yaml".format(ACCEPT_RELEASES[-1]))
    return parser.parse_args()


if __name__ == '__main__':
    _args = _parse_args()
    _source = _args.source
    _target = _args.target
    _values_path = _args.values
    _template_path = _args.template
    data = migrate(_source, _target, _values_path, _template_path)
    dump(data, _args.output)
