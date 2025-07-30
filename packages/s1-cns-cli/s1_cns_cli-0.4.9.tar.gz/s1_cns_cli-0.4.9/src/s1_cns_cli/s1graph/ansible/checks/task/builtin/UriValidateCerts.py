from __future__ import annotations

from s1_cns_cli.s1graph.ansible.checks.base_ansible_task_value_check import BaseAnsibleTaskValueCheck
from s1_cns_cli.s1graph.common.models.enums import CheckResult, CheckCategories


class UriValidateCerts(BaseAnsibleTaskValueCheck):
    def __init__(self) -> None:
        name = "Ensure that certificate validation isn't disabled with uri"
        id = "CKV_ANSIBLE_1"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.GENERAL_SECURITY,),
            supported_modules=("ansible.builtin.uri", "uri"),
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "validate_certs"


check = UriValidateCerts()
