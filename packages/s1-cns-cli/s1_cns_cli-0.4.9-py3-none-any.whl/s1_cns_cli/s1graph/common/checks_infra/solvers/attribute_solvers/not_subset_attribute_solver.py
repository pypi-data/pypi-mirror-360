from typing import Optional, Any, Dict

from s1_cns_cli.s1graph.common.checks_infra.solvers.attribute_solvers.subset_attribute_solver import SubsetAttributeSolver
from s1_cns_cli.s1graph.common.graph.checks_infra.enums import Operators


class NotSubsetAttributeSolver(SubsetAttributeSolver):
    operator = Operators.NOT_SUBSET  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
