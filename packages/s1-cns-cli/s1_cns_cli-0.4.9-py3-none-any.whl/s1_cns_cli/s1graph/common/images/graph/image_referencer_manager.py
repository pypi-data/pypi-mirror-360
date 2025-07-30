from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from s1_cns_cli.s1graph.common.images.image_referencer import Image
    from networkx import DiGraph


class GraphImageReferencerManager:
    __slots__ = ("graph_connector",)

    def __init__(self, graph_connector: DiGraph) -> None:
        self.graph_connector = graph_connector

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass
