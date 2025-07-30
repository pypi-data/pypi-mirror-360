from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from s1_cns_cli.s1graph.common.checks.base_check import BaseCheck
from s1_cns_cli.s1graph.common.util.tqdm_utils import ProgressBar

from s1_cns_cli.s1graph.common.output.report import Report
from s1_cns_cli.s1graph.policies_3d.checks_infra.base_check import Base3dPolicyCheck
from s1_cns_cli.s1graph.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from s1_cns_cli.s1graph.common.graph.graph_manager import GraphManager  # noqa


class BasePostRunner(ABC):
    check_type = ''  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        self.pbar = ProgressBar(self.check_type)

    @abstractmethod
    def run(
            self,
            checks: list[BaseCheck | Base3dPolicyCheck],
            scan_reports: list[Report],
            runner_filter: RunnerFilter | None = None
    ) -> Report:
        raise NotImplementedError()
