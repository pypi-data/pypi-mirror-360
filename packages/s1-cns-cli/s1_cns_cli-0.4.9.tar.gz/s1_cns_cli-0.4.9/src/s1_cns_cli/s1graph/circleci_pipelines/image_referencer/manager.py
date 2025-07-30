from __future__ import annotations
from typing import Any

from s1_cns_cli.s1graph.circleci_pipelines.image_referencer.provider import CircleCIProvider
from s1_cns_cli.s1graph.common.images.workflow.image_referencer_manager import WorkflowImageReferencerManager


class CircleCIImageReferencerManager(WorkflowImageReferencerManager):

    def __init__(self, workflow_config: dict[str, Any], file_path: str) -> None:
        provider = CircleCIProvider(workflow_config=workflow_config, file_path=file_path)
        super().__init__(workflow_config, file_path, provider)
