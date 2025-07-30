from s1_cns_cli.s1graph.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from s1_cns_cli.s1graph.common.parsers.node import DictNode
from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult


class RedShiftSSL(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Redshift uses SSL"
        id = "CKV_AWS_105"
        supported_resources = ["AWS::Redshift::ClusterParameterGroup"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: DictNode) -> CheckResult:
        params = conf.get("Properties", {}).get("Parameters", {})

        for param in params:
            if param.get("ParameterName") == "require_ssl":
                value = param.get("ParameterValue")
                if isinstance(value, bool):
                    value = str(value).lower()
                if value == "true":
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = RedShiftSSL()
