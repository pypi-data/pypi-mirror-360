from __future__ import annotations

from s1_cns_cli.s1graph.common.models.enums import CheckResult
from s1_cns_cli.s1graph.github.base_github_negative_branch_security import NegativeBranchSecurity


class GithubRequire2Approvals(NegativeBranchSecurity):
    def __init__(self) -> None:
        name = "Ensure any change to codescanner receives approval of two strongly authenticated users"
        id = "CKV_GITHUB_19"
        super().__init__(name=name, id=id, missing_attribute_result=CheckResult.FAILED)

    def get_evaluated_keys(self) -> list[str]:
        return ["required_pull_request_reviews/required_approving_review_count"]

    def get_forbidden_values(self) -> list[int | None]:
        return [None, 0, 1]


check = GithubRequire2Approvals()
