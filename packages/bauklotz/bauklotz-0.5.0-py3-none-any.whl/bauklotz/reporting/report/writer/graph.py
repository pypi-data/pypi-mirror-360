from typing import Self

from networkx.readwrite.gml import write_gml

from bauklotz.reporting.item.graph import Graph
from bauklotz.reporting.report import Report, ReportConfiguration
from bauklotz.reporting.types import JSONType


class GraphWriterConfiguration(ReportConfiguration):
    """
    GraphWriterConfiguration class handles the configuration settings specifically
    related to graph writing operations.

    The class provides mechanisms to initialize graph writer configurations and
    deserialize data to reconstruct its instance. It extends the functionalities
    of the ReportConfiguration class.

    Attributes:
        format (str): The file format to be used for writing the graph (e.g., 'gml').
    """
    def __init__(self, format_: str = 'gml') -> None:
        """
        Represents a class for handling a specific format.

        Attributes:
            format_ (str): The format to be utilized. Default value is 'gml'.
        """
        self.format = format_

    @classmethod
    def deserialize(cls, data: dict[str, JSONType]) -> Self:
        """
        Deserializes a dictionary into an instance of the class. The method extracts
        specific information from the input dictionary and uses it to create the
        class instance.

        Args:
            data (dict[str, JSONType]): A dictionary containing the data to be
                deserialized. The dictionary must include a key 'format' with
                corresponding value containing the format string.

        Returns:
            Self: An instance of the class initialized with the extracted data.
        """
        return cls(data.get('format', 'gml'))


class GraphWriterReport(Report[Graph, GraphWriterConfiguration]):
    """Handles the process of writing graph data to files.

    GraphWriterReport is responsible for saving graph objects to file using a specific
    format as defined by the provided configuration. Each graph is written to a file
    with a unique name based on the report's name and a running counter. This class
    utilizes the GraphWriterConfiguration to determine the output file format.

    Attributes:
        _file_counter (int): Counter to ensure unique file names for each graph saved.
    """
    def __init__(self, name: str, config: GraphWriterConfiguration):
        """
        Represents an initializer for a graph writer with specific configuration and
        state management.

        This class is responsible for initializing a graph writer object with a given
        name and configuration. It also manages internal state variables necessary
        for its operation. This implementation includes an internal counter to
        track specific operations.

        Args:
            name: The name of the graph writer object being initialized.
            config: The configuration object of type GraphWriterConfiguration
                to configure the graph writer.

        Attributes:
            _file_counter: An internal counter used to track the number of files
                processed or created by the graph writer.
        """
        super().__init__(name, config)
        self._file_counter: int = 0

    def write(self, item: Graph) -> None:
        """
        Writes a Graph object to a file in GML format.

        The method generates a filename using the object's name, a counter, and the
        configured file format. It then converts the provided graph to a NetworkX format
        and writes it to the file. The internal file counter is incremented after writing
        the file.

        Args:
            item (Graph): The graph object to be written to a file. This must be
                convertible to a NetworkX graph using its `to_networkx` method.
        """
        out: str = f'{self.name}_{self._file_counter}.{self.config.format}'
        write_gml(item.to_networkx(), out)
        self._file_counter += 1

