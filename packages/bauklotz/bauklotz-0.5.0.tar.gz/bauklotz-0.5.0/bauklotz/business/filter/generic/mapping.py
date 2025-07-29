from collections.abc import Callable
from functools import singledispatchmethod
from typing import Iterable, Self

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.reporting.item import Item
from bauklotz.reporting.item.graph import Graph, GraphNode
from bauklotz.reporting.types import JSONType


def _identity[T](item: T) -> T:
    return item


class ItemMapper[I: Item, O: Item]:
    def __init__(self, mapper: Callable[[I], O]):
        self.mapper = mapper

    def __call__(self, item: I) -> O:
        return self.mapper(item)


class MappingConfig[I: Item, O: Item](FilterConfig):
    mapper: ItemMapper[I, O] = ItemMapper(_identity)

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        pass



class MappingFilter[I: Item, O: Item, C: MappingConfig](Filter[I, O, MappingConfig[I, O]]):
    def __init__(self, name: str, config: MappingConfig[I, O]):
        super().__init__(name, config)

    def process(self, item: I) -> Iterable[O]:
        yield self.config.mapper(item)



class GraphBuilderConfig(FilterConfig):
    def __init__(self, neighbors: Iterable[str], label: str | None = None):
        self._neighbors: set[str] = set(neighbors)
        self._label: str | None = label

    @property
    def label(self) -> str | None:
        return self._label

    @property
    def neighbors(self) -> set[str]:
        return set(self._neighbors)

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data['neighbors'].split(','))


class GraphBuilderFilter[I: Item](Filter[I, Graph, GraphBuilderConfig]):
    def __init__(self, name: str, config: GraphBuilderConfig):
        super().__init__(name, config)
        self._graph: Graph = Graph()
        self._items: list[I] = list()

    def process(self, item: I) -> Iterable[Graph]:
        self._items.append(item)
        return ()

    def close(self) -> Iterable[Graph]:
        for item in self._items:
            node: GraphNode = GraphNode(item.id, )
            self._graph.add_node(node)
        yield self._graph


    @singledispatchmethod
    def _get_info_from_item(self, info, item: I) -> JSONType:
        return getattr(item, info)

    @_get_info_from_item.register
    def _get_info_from_item_default(self, info: Callable, item: I) -> JSONType:
        return info(item)