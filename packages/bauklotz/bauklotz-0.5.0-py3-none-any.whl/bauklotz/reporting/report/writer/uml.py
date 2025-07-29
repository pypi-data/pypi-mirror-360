from typing import Self

from bauklotz.reporting.item.python.definition import PythonClass
from bauklotz.reporting.report import ReportConfiguration
from bauklotz.reporting.report.buffered import BufferedReport
from bauklotz.reporting.types import JSONType


class ClassDiagramConfiguration(ReportConfiguration):
    """Configuration class used to handle settings for a class diagram.

    This class is designed to encapsulate configuration details required
    to generate a class diagram, such as the file path for saving the diagram
    and the resolution (DPI). It supports serialization and deserialization
    to and from dictionary-like data structures for easy storage and retrieval.

    Attributes:
        _path (str): The file path where the class diagram will be saved.
        _dpi (int): The resolution of the class diagram image in dots per inch (DPI).
    """
    def __init__(self, path: str, dpi: int = 500):
        """
        Represents an example class that initializes with a file path and a DPI
        (dots per inch) value.

        Attributes:
            _path (str): The file path provided during initialization.
            _dpi (int): The DPI value provided during initialization, defaults to 500
                if not specified.
        """
        self._path: str = path
        self._dpi: int = dpi

    @property
    def path(self) -> str:
        """
        Returns the path attribute of the object.

        Attributes:
            path (str): The file system path associated with the object.

        Returns:
            str: The current value of the `_path` attribute.
        """
        return self._path

    @property
    def dpi(self) -> int:
        """
        Returns the DPI (dots per inch) value.

        The DPI value determines the resolution or clarity of an image, typically used
        to specify the quality of prints.

        Returns:
            int: The current DPI value.
        """
        return self._dpi

    @classmethod
    def deserialize(cls, data: dict[str, JSONType]) -> Self:
        """
        Deserializes a dictionary containing image settings into an instance of the class.

        This method is used to reconstruct an instance of the class from dictionary
        data, typically when reading information from external sources such as APIs
        or configuration files.

        Args:
            data (dict[str, JSONType]): A dictionary containing serialized image
                properties. It must have the key `path` specifying the image path and
                optionally the key `dpi` indicating the resolution.

        Returns:
            Self: An instance of the class created using the provided dictionary data.
        """
        return cls(data['path'], data.get('dpi', 500))


class ClassDiagramWriter(BufferedReport[PythonClass, ClassDiagramConfiguration]):
    """
    Manages the generation and writing of class diagrams in the PlantUML format.

    This class is responsible for creating class diagrams based on the provided
    Python class data and configuration. It formats the syntax according to
    PlantUML standards and writes the output to a specified file.

    Attributes:
        _connections (list[str]): Stores connections (e.g., inheritance, associations)
            between classes in the diagram.
    """
    def __init__(self, name: str, config: ClassDiagramConfiguration):
        """
        Initializes a new instance of the class with specified name and configuration.

        Args:
            name: A string representing the name of the instance.
            config: An instance of ClassDiagramConfiguration providing the configuration
                for the class diagram.

        Attributes:
            _connections: A list of strings representing the connections associated
                with the instance.
        """
        super().__init__(name, config)
        self._connections: list[str] = list()

    def close(self) -> None:
        """
        Closes and finalizes the writing operation by generating a PlantUML diagram file.

        The method processes a list of classes and their connections, converts them into a
        PlantUML-compatible format, and writes the resulting content into a file defined
        by the configuration. It ensures the proper structure and syntax of the PlantUML
        document.

        Args:
            None

        Returns:
            None
        """
        body: list[str] = ['@startuml', f'skinparam dpi {self.config.dpi}', 'top to bottom direction']
        body.extend(map(self._handle_class, self._get_entries()))
        body.extend(self._connections)
        body.append('@enduml')
        with open(self.config.path, 'w') as out:
            out.write('\n'.join(body))

    def _handle_class(self, item: PythonClass) -> str:
        class_type: str = 'class'
        if item.facts.get('abstract'):
            class_type = 'abstract'
        if item.facts.get('protocol'):
            class_type = 'protocol'
        body: list[str] = list()
        body.append(f'{class_type} {item.module}.{item.name} {{')
        for method in item.methods:
            args = ', '.join(arg['name'] for arg in method.args)
            body.append(f'\t+{method.name}({args})')
        body.append('}')
        for superclass in item.facts.get('superclass', []):
            self._connections.append(f'{item.name} <|-- {superclass}')
        return '\n'.join(body)



