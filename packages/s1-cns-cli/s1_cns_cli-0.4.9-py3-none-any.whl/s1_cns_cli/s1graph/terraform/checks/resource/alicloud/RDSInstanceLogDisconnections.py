from s1_cns_cli.s1graph.terraform.checks.resource.alicloud.AbsRDSParameter import AbsRDSParameter


class RDSInstanceLogDisconnections(AbsRDSParameter):
    def __init__(self):
        super().__init__(check_id="CKV_ALI_36", parameter="log_disconnections")


check = RDSInstanceLogDisconnections()
