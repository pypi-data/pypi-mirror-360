from typing import Optional, Any, Dict

from s1_cns_cli.s1graph.common.graph.checks_infra.enums import Operators
from .contains_attribute_solver import ContainsAttributeSolver


class NotContainsAttributeSolver(ContainsAttributeSolver):
    operator = Operators.NOT_CONTAINS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
