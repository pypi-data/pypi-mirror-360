from s1_cns_cli.s1graph.kubernetes.checks.resource.base_rbac_check import BaseRbacK8sCheck, RbacOperation


class RbacBindRoleBindings(BaseRbacK8sCheck):
    def __init__(self):
        name = "Minimize Roles and ClusterRoles that grant permissions to bind RoleBindings or ClusterRoleBindings"
        id = "CKV_K8S_157"
        super().__init__(name=name, id=id)

        self.failing_operations = [
            RbacOperation(
                apigroups=["rbac.authorization.kubernetes.io"],
                verbs=["bind"],
                resources=["rolebindings", "clusterrolebindings"]
            ),
        ]


check = RbacBindRoleBindings()
