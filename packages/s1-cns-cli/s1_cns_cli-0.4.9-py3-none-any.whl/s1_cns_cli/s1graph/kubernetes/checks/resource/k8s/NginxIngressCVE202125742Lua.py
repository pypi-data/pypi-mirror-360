from typing import Dict, Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_spec_check import BaseK8Check
from s1_cns_cli.s1graph.common.util.type_forcers import force_list
import re


class NginxIngressCVE202125742Lua(BaseK8Check):
    def __init__(self) -> None:
        name = "Prevent NGINX Ingress annotation snippets which contain LUA codescanner execution. See CVE-2021-25742"
        id = "CKV_K8S_152"
        supported_kind = ("Ingress",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf: Dict[str, Any]) -> CheckResult:
        badInjectionPatterns = "\\blua_|_lua\\b|_lua_|\\bkubernetes\\.io\\b"

        if conf["metadata"]:
            if conf["metadata"].get("annotations"):
                for annotation in force_list(conf["metadata"]["annotations"]):
                    for key, value in annotation.items():
                        if "snippet" in key and re.search(badInjectionPatterns, value):
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = NginxIngressCVE202125742Lua()
