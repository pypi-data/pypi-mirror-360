import re

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck

# Default Compute -compute@developer.gserviceaccount.com
# Default App Spot @appspot.gserviceaccount.com
DEFAULT_SA = re.compile(r".*-compute@developer\.gserviceaccount\.com|.*@appspot\.gserviceaccount\.com")


class AbsGoogleIAMMemberDefaultServiceAccount(BaseResourceCheck):
    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['members'] if 'members' in conf else ['member']
        members_conf = conf['members'][0] if 'members' in conf else conf.get('member', [])
        if any(re.match(DEFAULT_SA, str(member)) for member in members_conf):
            return CheckResult.FAILED
        return CheckResult.PASSED
