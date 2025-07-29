from abc import ABC, abstractmethod
from inspect import signature
from typing import Self

from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType


class ReportConfiguration(ABC):
    """
    Represents an abstract base class for report configuration.

    This class serves as a blueprint for creating specific report configuration
    implementations. Each subclass must provide an implementation of the
    `deserialize` method to handle the conversion of a structured dictionary
    object into an instance of the subclass.

    Attributes:
        None.
    """

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict[str, JSONType]) -> Self:
        """
        Deserializes a dictionary into an instance of the class.

        This method is an abstract method and must be implemented in any subclass.
        It allows the transformation of a dictionary representation of the object
        into an actual instance of the class. Deserialization is specifically useful
        when converting JSON-like structures received from APIs or other storage
        mechanisms into domain models.

        Args:
            data (dict[str, JSONType]): The dictionary containing serialized data
                to be converted into an instance of the class.

        Returns:
            Self: An instance of the class deserialized from the dictionary.
        """



class Report[I: Item, C: ReportConfiguration](ABC):
    """
    Represents an abstract base class for creating reports with items.

    The `Report` class serves as a blueprint for report generation. It provides
    a common interface and enforces the implementation of the `write` method by
    subclasses. The class includes attributes and methods for managing the report
    name and defining behavior for writing and closing the report.

    Attributes:
        name (str): The name of the report.
    """
    def __init__(self, name: str, config: C):
        self._name: str = name
        self._config: C = config

    @property
    def config(self) -> C:
        """
        Returns the configuration object associated with the instance.

        The configuration object encapsulates the settings or parameters
        that define the behavior of the instance. Accessing this property
        provides a read-only view of the current configuration.

        Attributes:
            config: Represents the configuration object stored within
                the instance.

        Returns:
            C: The configuration object associated with the instance.
        """
        return self._config

    @classmethod
    def config_type(cls) -> type[ReportConfiguration]:
        """
            Determines and returns the type of the configuration object that should be used
            with the class. This method inspects the type hints of the `__init__` method
            for the `config` parameter to deduce the expected configuration type.

            Returns:
                type[ReportConfiguration]: The type of the expected configuration object.
        """
        return signature(cls.__init__).parameters.get('config').annotation

    @property
    def name(self) -> str:
        """
        Gets the name attribute for the object.

        This property retrieves the private `_name` attribute and provides
        read-only access to its value. It is commonly used for getting the
        name identifier of an instance.

        Returns:
            str: The name associated with the object.
        """
        return self._name

    @abstractmethod
    def write(self, item: I) -> None:
        """
        Represents an abstract class for objects that implement a write operation.

        This class is intended to be subclassed to provide concrete implementations of
        a write operation, which takes in a single item and performs some action or
        operation with it.

        Methods:
            write: Abstract method that must be implemented in subclasses to define the
                behavior of the write operation.
        """


    def close(self) -> None:
        """
        Closes the current resource or connection.

        This method is responsible for ensuring that any open resources or connections
        associated with the object are properly closed and cleaned up. It should be
        called when the object is no longer needed to release any underlying system
        resources such as file handles, database connections, or network sockets.

        Raises:
            OSError: If an error occurs while closing the resource.
        """
        return None