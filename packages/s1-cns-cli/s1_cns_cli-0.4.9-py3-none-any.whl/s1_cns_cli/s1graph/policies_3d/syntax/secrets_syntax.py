import abc

from s1_cns_cli.s1graph.common.output.record import Record
from s1_cns_cli.s1graph.policies_3d.syntax.syntax import Predicate


class SecretsPredicate(Predicate):
    def __init__(self, record: Record) -> None:
        super().__init__()
        self.record = record

    @abc.abstractmethod
    def __call__(self) -> bool:
        raise NotImplementedError()
