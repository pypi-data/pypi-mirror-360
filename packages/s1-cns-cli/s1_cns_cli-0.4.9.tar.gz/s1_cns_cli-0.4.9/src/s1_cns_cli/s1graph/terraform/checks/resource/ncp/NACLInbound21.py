from s1_cns_cli.s1graph.terraform.checks.resource.ncp.NACLInboundCheck import NACLInboundCheck


class NACLInbound21(NACLInboundCheck):
    def __init__(self):
        super().__init__(check_id="CKV_NCP_9", port=21)


check = NACLInbound21()
