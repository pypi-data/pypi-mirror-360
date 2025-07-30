from typing import Optional, Any, Dict

from s1_cns_cli.s1graph.common.graph.checks_infra.enums import Operators
from .ending_with_attribute_solver import EndingWithAttributeSolver


class NotEndingWithAttributeSolver(EndingWithAttributeSolver):
    operator = Operators.NOT_ENDING_WITH  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        return not super()._get_operation(vertex, attribute)
