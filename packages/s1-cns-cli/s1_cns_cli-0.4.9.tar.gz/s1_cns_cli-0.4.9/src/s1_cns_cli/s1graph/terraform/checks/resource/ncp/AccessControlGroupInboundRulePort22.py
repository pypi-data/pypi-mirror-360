from s1_cns_cli.s1graph.terraform.checks.resource.ncp.AccessControlGroupInboundRule import AccessControlGroupInboundRule


class AccessControlGroupRuleInboundPort22(AccessControlGroupInboundRule):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_4", port=22)


check = AccessControlGroupRuleInboundPort22()
