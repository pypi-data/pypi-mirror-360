from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AMILaunchIsShared(BaseResourceCheck):
    def __init__(self):
        name = "Ensure to Limit AMI launch Permissions"
        id = "CKV_AWS_205"
        supported_resources = ['aws_ami_launch_permission']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        return CheckResult.FAILED


check = AMILaunchIsShared()
