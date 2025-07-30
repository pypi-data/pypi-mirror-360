from typing import Dict, List, Any

from s1_cns_cli.s1graph.common.util.type_forcers import force_list
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult


class SecretManagerSecretEncrypted(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that Secrets Manager secret is encrypted using KMS CMK"
        id = "CKV_AWS_149"
        supported_resources = ["aws_secretsmanager_secret"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        aws_kms_alias = 'aws/'
        kms_key_id = force_list(conf.get('kms_key_id', []))
        if not kms_key_id or not kms_key_id[0]:
            return CheckResult.FAILED
        else:
            return CheckResult.FAILED if aws_kms_alias in kms_key_id[0] else CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['kms_key_id']


check = SecretManagerSecretEncrypted()
