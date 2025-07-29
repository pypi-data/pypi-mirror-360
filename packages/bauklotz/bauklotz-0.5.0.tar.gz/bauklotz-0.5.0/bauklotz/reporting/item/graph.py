from collections.abc import Iterable
from enum import Enum
from typing import Self

from networkx import Graph as NXGraph
from networkx.classes import DiGraph
from networkx.readwrite.json_graph.node_link import node_link_data
from toolz import dissoc

from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType

_LABEL_KEY = 'label'
_TYPE_KEY = 'type'


class GraphType(Enum):
    """Enumeration for graph types.

    Detailed description of the GraphType enumeration. It is used to classify
    graphs as either directed or undirected.

    Attributes:
        DIRECTED (DiGraph): Represents a directed graph.
        UNDIRECTED (NXGraph): Represents an undirected graph.
    """
    DIRECTED = DiGraph
    UNDIRECTED = NXGraph


class GraphNode:
    """Represents a node within a graph structure.

    GraphNode encapsulates the properties and attributes associated with a node
    in a graph, including its unique identifier, label, type, and any additional
    attributes provided as key-value pairs. This class is designed to facilitate
    storage, retrieval, and access to node-related data.

    Attributes:
        _id (str): Unique identifier of the graph node.
        _label (str): Label associated with the graph node.
        _type (str): Type categorization of the graph node.
        _attributes (dict[str, JSONType]): Arbitrary key-value pairs representing additional
            attributes of the graph node.
    """
    def __init__(self, node_id: str, label: str, node_type: str, **attributes: JSONType):
        self._id: str = node_id
        self._label: str = label
        self._type: str = node_type
        self._attributes: dict[str, JSONType] = attributes

    @property
    def id(self) -> str:
        """
        Represents a property that retrieves a unique identifier.

        The `id` property is used to access the unique identifier associated with the
        object. This identifier is immutable and is intended to serve as the primary
        key or reference for the object's instance.

        Attributes:
            _id (str): The private attribute storing the unique identifier.

        Returns:
            str: The unique identifier associated with the instance.
        """
        return self._id

    @property
    def label(self) -> str:
        """
        Gets the label of the entity.

        The label represents a descriptive text or name associated with the entity. This is typically used for display purposes
        and should be concise and meaningful.

        Returns:
            str: The label of the entity.
        """
        return self._label

    @property
    def type(self) -> str:
        """
        Gets the type of the object.

        This property retrieves the `_type` attribute of the object. The type
        indicates the specific category or classification associated with the instance.

        Returns:
            str: The type of the object.
        """
        return self._type

    @property
    def attributes(self) -> dict[str, JSONType]:
        """
        Represents a property method that provides access to the internal attributes
        of the object as a dictionary with string keys and values of type JSONType.

        Returns:
            dict[str, JSONType]: A dictionary containing the attributes of the object
            where the keys are strings and the values conform to the type JSONType.
        """
        return self._attributes

    def __getitem__(self, item: str) -> JSONType:
        return self._attributes[item]

class Graph(Item):
    """
    Represents a graph structure with support for node and edge management, and serialization.

    The Graph class provides functionality to create and manipulate a graph structure
    consisting of nodes and edges. Nodes are uniquely identified and can include
    associated properties or metadata. Edges define connections between nodes and
    can also include additional attributes. The graph can be serialized for data
    persistence or shared between systems and cloned for independent manipulation.

    Attributes:
        _type (GraphType): The type of the graph, such as directed or undirected,
            determined at initialization.
        _graph (NXGraph): The internal graph representation utilized to handle
            nodes and edges, leveraging NetworkX.
    """
    def __init__(self, mode: GraphType = GraphType.DIRECTED):
        self._type: GraphType = mode
        self._graph: NXGraph = mode.value()
        super().__init__()

    @property
    def id(self) -> str:
        return str(self)

    def add_node(self, node: GraphNode) -> None:
        """
        Adds a node to the internal graph representation with its attributes.

        The node is uniquely identified by its ID and additional properties such as
        label, type, and custom attributes are stored in the graph data structure.
        This method modifies the internal structure of the graph being managed by
        the class instance.

        Args:
            node: An instance of GraphNode that encapsulates the unique identifier,
                label, type, and any additional attributes of the node to be added
                to the graph.
        """
        self._graph.add_node(node.id, label=node.label, type=node.type, **node.attributes)

    def connect_nodes(self, source: str, target: str, **attributes: JSONType) -> None:
        """
        Connects two nodes in the graph by adding an edge between them.

        This method adds an edge from the `source` node to the `target` node
        within the graph structure. Additional attributes for the edge can
        be specified as keyword arguments. The `attributes` can include
        optional metadata or information relevant to this edge in the graph.

        Args:
            source (str): The identifier of the source node in the graph.
            target (str): The identifier of the target node in the graph.
            **attributes (JSONType): Arbitrary keyword arguments representing
                attributes to store on the edge.

        """
        self._graph.add_edge(source, target, **attributes)

    def get_nodes_by_type(self, node_type: str) -> Iterable[GraphNode]:
        """
        Fetches nodes of a specific type from the graph.

        This method iterates through all the nodes in the graph and filters nodes
        based on the specified type. For each matching node, the method yields a
        GraphNode instance, which includes metadata from the graph node.

        Args:
            node_type (str): The type of nodes to filter.

        Yields:
            GraphNode: A GraphNode instance containing the node ID, label, type,
            and additional metadata associated with the graph node.
        """
        for node in self._graph.nodes:
            if self._graph.nodes[node]['type'] == node_type:
                yield GraphNode(
                    node,
                    self._graph.nodes[node][_LABEL_KEY],
                    self._graph.nodes[node][_TYPE_KEY],
                    **dissoc(self._graph.nodes[node], _LABEL_KEY, _TYPE_KEY)
                )


    def serialize(self) -> JSONType:
        """
        Serializes the graph object into a JSON compatible format.

        This method converts the internal graph representation into a format
        that can be easily serialized into JSON. It uses the `node_link_data`
        function to achieve the conversion. The resulting data structure can
        be utilized for purposes such as saving the graph state or data
        persistence.

        Returns:
            JSONType: A JSON compatible representation of the underlying
            graph structure.
        """
        return node_link_data(self._graph)

    def clone(self) -> Self:
        """
        Creates and returns a deep copy of the Graph object.

        This method generates a new Graph object that copies the structure
        and data of the current Graph instance. The copied graph will be
        independent, with no shared references to the original object's
        internal structures.

        Returns:
            Self: A new Graph instance that is a deep copy of the original.
        """
        copy: Graph = Graph(self._type)
        copy._graph = self._graph.copy()
        return copy

    def to_networkx(self) -> NXGraph:
        """
        Converts the internal graph representation into a NetworkX graph instance.

        This method provides access to the graph represented internally in the
        class as a NetworkX graph object, enabling further processing or analysis
        using the NetworkX library.

        Returns:
            NXGraph: The internal graph in the form of a NetworkX graph object.
        """
        return self._graph

    def __contains__(self, item: str | GraphNode) -> bool:
        if isinstance(item, GraphNode):
            return item.id in self._graph.nodes
        return item in self._graph.nodes