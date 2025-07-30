from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, Any, Optional

from s1_cns_cli.s1graph.common.checks.base_check import BaseCheck
from s1_cns_cli.s1graph.common.models.enums import CheckCategories, CheckResult
from s1_cns_cli.s1graph.common.multi_signature import multi_signature
from s1_cns_cli.s1graph.kubernetes.checks.resource.registry import registry


class BaseK8Check(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_entities: "Iterable[str]",
        guideline: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type="k8",
            guideline=guideline
        )
        self.supported_specs = supported_entities
        registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        self.entity_type = entity_type
        return self.scan_spec_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_spec_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        """Return result of Kubernetes object check."""
        raise NotImplementedError()

    @classmethod
    @scan_spec_conf.add_signature(args=["self", "conf"])
    def _scan_spec_conf_self_conf(cls, wrapped):
        def wrapper(self, conf, entity_type=None):
            # keep default argument for entity_type so old codescanner, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper

    @staticmethod
    def get_inner_entry(conf: Dict[str, Any], entry_name: str) -> Dict[str, Any]:
        spec = {}
        if conf.get("spec") and isinstance(conf["spec"], dict) and conf.get("spec").get("template"):
            spec = conf.get("spec").get("template").get(entry_name, {})
        return spec
