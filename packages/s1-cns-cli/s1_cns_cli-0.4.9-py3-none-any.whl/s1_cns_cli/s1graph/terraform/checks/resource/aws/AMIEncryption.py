from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AMIEncryptionWithCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure AMIs are encrypted using KMS CMKs"
        id = "CKV_AWS_204"
        supported_resources = ['aws_ami']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get('ebs_block_device'):
            mappings = conf.get('ebs_block_device')
            for mapping in mappings:
                if not mapping.get("snapshot_id"):
                    if not mapping.get("encrypted"):
                        return CheckResult.FAILED
                    if mapping.get("encrypted")[0] is False:
                        return CheckResult.FAILED
        # pass thru
        return CheckResult.PASSED


check = AMIEncryptionWithCMK()
