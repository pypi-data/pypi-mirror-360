from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck

BASIC_ROLES = {
    "roles/owner",
    "roles/editor",
    "roles/viewer",
}


class AbsGoogleBasicRoles(BaseResourceCheck):
    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['role']
        role = conf.get("role")
        if role and isinstance(role, list) and role[0] in BASIC_ROLES:
            return CheckResult.FAILED
        return CheckResult.PASSED
