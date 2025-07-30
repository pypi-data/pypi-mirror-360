from typing import Optional, Any, Dict
from collections.abc import Sized
from s1_cns_cli.s1graph.common.graph.checks_infra.enums import Operators
from s1_cns_cli.s1graph.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class IsEmptyAttributeSolver(BaseAttributeSolver):
    operator = Operators.IS_EMPTY  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None

        if isinstance(attr, (list, Sized)):
            return len(attr) == 0

        return False
