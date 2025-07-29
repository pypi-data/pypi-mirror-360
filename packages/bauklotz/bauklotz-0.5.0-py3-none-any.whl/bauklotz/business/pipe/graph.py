from collections import deque, defaultdict
from collections.abc import Iterable, Sequence
from functools import singledispatchmethod

from networkx import DiGraph
from networkx.classes import neighbors
from networkx.readwrite.gml import write_gml

from bauklotz.business.filter import Filter, FilterConfig
from bauklotz.business.filter.generic.mapping import MappingFilter, MappingConfig
from bauklotz.business.pipe import Pipe
from bauklotz.reporting.item import Item
from bauklotz.reporting.logging import BauklotzLogger
from bauklotz.reporting.report import ReportConfiguration, Report


class GraphPipe(Pipe):
    def __init__(self, logger: BauklotzLogger | None = None):
        self._graph: DiGraph = DiGraph()
        super().__init__(logger)


    def inject(self, item: Item, channel: str) -> None:
        self._has_node_of_type(channel, "input")
        self._logger.info(f"Injecting item {item} into channel {channel}.")
        self._graph.nodes[channel]['queue'].append(item)
        self._pump_items()


    def wire(self, channel_name: str, filter_: Filter[Item, Item, FilterConfig]) -> None:
        self._has_node_of_type(channel_name, "input")
        self._has_node_of_type(filter_.name, "filter")
        self._graph.add_edge(channel_name, filter_.name)


    def connect[I: Item](
            self,
            filter_: Filter[Item, I, FilterConfig],
            end: Report[I, ReportConfiguration] | Filter[I, Item, FilterConfig],
            labels: set[str] | None = None
    ) -> None:
        self._has_node_of_type(filter_.name, "filter")
        self._has_node_of_type(end.name, {"report", "filter"})
        self._graph.add_edge(filter_.name, end.name, labels=sorted(labels or set()))

    def add_report(self, report: Report[Item, ReportConfiguration]) -> None:
        self._add_node(report.name, "report", filter=report, queue=deque())

    def add_filter(self, filter_: Filter[Item, Item, FilterConfig]) -> None:
        self._add_node(filter_.name, "filter", filter=filter_, queue=deque())

    def add_input_channel(self, name: str) -> None:
        self._add_node(name, "input", filter=MappingFilter(name, MappingConfig()), queue=deque())


    def close(self) -> None:
        self._logger.info(f"Closing pipe.")
        while self._graph:
            for name in tuple(node for node, degree in self._graph.in_degree() if degree == 0):
                node = self._graph.nodes[name]
                self._logger.info(f"Closing node {name}")
                self._handle_node_output(name, node["filter"].close())
                self._graph.remove_node(name)
            self._pump_items()


    def _pump_items(self) -> None:
        while True:
            for node in self._graph.nodes:
                self._handle_node_input(node)
            if len(self) == 0:
                break

    def _handle_node_output[I: Item](self, source: str, output: Iterable[I] | None) -> None:
        upstream_entities: Sequence[str] = tuple(neighbors(self._graph, source))
        for item in output if output else ():
            self._logger.info(f"Item {item} produced by filter {source}.")
            for upstream in upstream_entities:
                if self._is_not_filtered_by_label(source, upstream, item):
                    self._graph.nodes[upstream]['queue'].append(item)


    def _is_not_filtered_by_label(self, source: str, target: str, item: Item) -> bool:
        graph_labels: set[str] = set(self._graph.edges[source, target].get('labels', {}))
        if not graph_labels:
            return True
        else:
            return any(label in item.labels for label in graph_labels)



    def _handle_node_input(self, node: str) -> None:
        for item in self._graph.nodes[node]['queue']:
            self._handle_node_output(node, self._handle_item_input(self._graph.nodes[node]['filter'], item))
        self._graph.nodes[node]['queue'].clear()

    @singledispatchmethod
    def _handle_item_input(self, node, item: Item) -> Iterable[Item]:
        """

        Args:
            node:
            item:

        Returns:

        """
        raise TypeError(f"Unsupported item type {type(item)} for node {node}.")

    @_handle_item_input.register
    def _(self, node: Filter, item: Item) -> Iterable[Item]:
        self._logger.info(f"Processing item {item} with filter {node.name}.")
        return node.process(item)

    @_handle_item_input.register
    def _(self, node: Report, item: Item) -> Iterable[Item]:
        self._logger.info(f"Reporting item {item} with filter {node.name}.")
        node.write(item)
        return ()


    def __len__(self) -> int:
        return sum(len(attributes['queue']) for _, attributes in self._graph.nodes(data=True))


    def _add_node(self, name: str, node_type: str, **attributes) -> None:
        if name in self._graph.nodes:
            raise ValueError(f"Node with name {name} already exists.")
        self._graph.add_node(name, type=node_type, **attributes)

    def _has_node_of_type(self, name: str, required_type: str | set[str]):
        acceptable_types: set[str] = {required_type} if isinstance(required_type, str) else required_type
        if name not in self._graph.nodes:
            raise NameError(f"Node with name {name} does not exist.")
        if self._graph.nodes[name]["type"] not in acceptable_types:
            raise TypeError(f"Node with name {name} is not of type {required_type}.")

    def visualize(self, filename: str) -> str:
        visual_graph: DiGraph = DiGraph()
        for node, data in self._graph.nodes(data=True):
            entity = data.get('filter', None)
            entity_name: str = type(entity).__name__ if entity else "Input"
            visual_graph.add_node(node, type=data['type'], entity=entity_name)
        for src, target, data in self._graph.edges(data=True):
            visual_graph.add_edge(src, target, labels=data.get('labels', []))
        filename = f"{filename}.gml"
        write_gml(visual_graph, filename)
        return filename