from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.kubernetes.checks.resource.base_spec_check import BaseK8Check


class MinimizeCapabilitiesPSP(BaseK8Check):

    def __init__(self):
        # CIS-1.5 5.2.9
        name = "Minimize the admission of containers with capabilities assigned"
        # Location: PodSecurityPolicy.spec.requiredDropCapabilities
        id = "CKV_K8S_36"
        supported_kind = ['PodSecurityPolicy']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_kind)

    def scan_spec_conf(self, conf):
        if "spec" in conf:
            if "requiredDropCapabilities" in conf["spec"]:
                if conf["spec"]["requiredDropCapabilities"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = MinimizeCapabilitiesPSP()
