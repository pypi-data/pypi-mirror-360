from typing import Dict, List, Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.common.util.type_forcers import force_list
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class FirewallIngressOpen(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure the firewall ingress is not wide open"
        id = "CKV_DIO_4"
        supported_resources = ["digitalocean_firewall"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        self.evaluated_keys = ["inbound_rule"]
        inbound_rules = conf.get("inbound_rule")
        if inbound_rules:
            for rule in force_list(inbound_rules[0]):
                if not rule:
                    continue
                sources = rule.get("source_addresses")
                if sources:
                    for idx, source in enumerate(sources[0]):
                        self.evaluated_keys = [f"inbound_rule/[0]/source_addresses/[{idx}]"]
                        if source in ("0.0.0.0/0", "::/0"):
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = FirewallIngressOpen()
