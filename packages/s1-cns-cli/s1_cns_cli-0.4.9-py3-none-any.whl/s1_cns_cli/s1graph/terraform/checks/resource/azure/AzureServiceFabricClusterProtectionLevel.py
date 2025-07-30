from typing import Dict, List, Any

from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.common.util.type_forcers import force_list
from s1_cns_cli.s1graph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureServiceFabricClusterProtectionLevel(BaseResourceCheck):
    def __init__(self):
        name = "Ensures that Service Fabric use three levels of protection available"
        id = "CKV_AZURE_125"
        supported_resources = ['azurerm_service_fabric_cluster']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        self.evaluated_keys = ['fabric_settings']
        settings_conf = force_list(conf.get('fabric_settings'))
        for setting in settings_conf:
            if setting and setting.get('name') == ['Security']:
                params = setting.get('parameters', [{}])[0]
                if params.get('name') == 'ClusterProtectionLevel' and params.get('value') == 'EncryptAndSign':
                    index = settings_conf.index(setting)
                    self.evaluated_keys = [f'fabric_settings/[{index}]/parameters/[0]/name',
                                           f'fabric_settings/[{index}]/parameters/[0]/value']
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = AzureServiceFabricClusterProtectionLevel()
