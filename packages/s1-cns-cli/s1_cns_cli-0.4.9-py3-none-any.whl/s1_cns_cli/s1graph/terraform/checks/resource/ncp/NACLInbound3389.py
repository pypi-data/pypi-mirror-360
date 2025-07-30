from s1_cns_cli.s1graph.terraform.checks.resource.ncp.NACLInboundCheck import NACLInboundCheck


class NACLInbound3389(NACLInboundCheck):
    def __init__(self) -> None:
        super().__init__(check_id="CKV_NCP_11", port=3389)


check = NACLInbound3389()
