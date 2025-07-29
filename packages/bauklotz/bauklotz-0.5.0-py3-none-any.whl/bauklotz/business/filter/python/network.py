from math import log
from typing import Self, Iterable

from toolz import first

from bauklotz.business.filter import Filter, FilterConfig
from bauklotz.reporting.item.graph import Graph, GraphNode
from bauklotz.reporting.item.python.dependency import PythonImport
from bauklotz.reporting.types import JSONType


class DependencyNetworkConfig(FilterConfig):
    def __init__(self, log_weight: bool = False):
        self._log_weight: bool = log_weight

    @property
    def log_weight(self) -> bool:
        return self._log_weight

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data.get('log_weight', False))


class DependencyNetworkFilter(Filter[PythonImport, Graph, DependencyNetworkConfig]):
    def __init__(self, name: str, config: DependencyNetworkConfig):
        super().__init__(name, config)
        self._graph: Graph = Graph()
        self._items: list[PythonImport] = list()

    def process(self, item: PythonImport) -> Iterable[Graph]:
        self._items.append(item)
        return ()

    def close(self) -> Iterable[Graph]:
        for item in self._items:
            node: GraphNode = GraphNode(
                item.dependant.module_name,
                'internal',
                'module',
                module_type='project'
            )
            self._graph.add_node(node)
        for item in self._items:
            category: str = first(item.import_category().values())
            if item.dependency_id not in self._graph:
                self._graph.add_node(
                    GraphNode(
                        item.dependency_id,
                        'external',
                        'module',
                        module_type=category
                    )
                )
            self._graph.connect_nodes(
                item.dependant.module_name,
                item.dependency_id,
                weight=self._calculate_weight(len(item.imported_artifacts))
            )
        yield self._graph

    def _calculate_weight(self, import_count: int) -> int | float:
        return log(import_count + 1, 2) if self.config.log_weight else import_count