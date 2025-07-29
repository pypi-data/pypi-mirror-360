from abc import ABC, abstractmethod
from collections.abc import Iterable
from inspect import signature
from typing import get_args, Self
from types import UnionType

from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType


class FilterConfig(ABC):
    """
    Represents a base class for managing filter configuration deserialization.

    This abstract base class outlines the structure for deserializing JSON-like
    data into filter configuration instances. It serves as a blueprint for derived
    classes to implement specific deserialization logic based on their individual
    requirements, promoting consistent behavior and a standardized contract for
    handling configuration data.

    Attributes:
        None
    """
    @classmethod
    @abstractmethod
    def deserialize(cls, data: JSONType) -> Self:
        """
        Deserializes a JSON-like structure into an instance of the class.

        This method is expected to be implemented by subclasses to handle the logic
        of converting a JSON-like structure (`data`) into an instance of the respective
        class. The implementation must comply with the specific requirements of the
        class.

        Args:
            data: JSONType instance representing the serialized representation of the
                object to be deserialized.

        Returns:
            Self: An instance of the class that has been created and populated with
                data from the provided serialized format.

        Raises:
            NotImplementedError: If the method is called directly on a class that has
                not implemented this method, as it is intended to be overridden in
                subclasses.
        """



class Filter[I: Item, O: Item, C: FilterConfig](ABC):
    """
    Abstract base class for creating a filter that processes items.

    This class serves as a blueprint for creating filters that take in input items,
    process them, and return output items, while being configured using a specified
    filter configuration. The `Filter` class operates on generic types for input,
    output, and configuration.

    Attributes:
        _name (str): Name of the filter.
        _config (C): Configuration object for the filter.
    """

    provides_facts: frozenset[str] = frozenset()
    requires_facts: frozenset[str] = frozenset()

    def __init__(self, name: str, config: C):
        self._name: str = name
        self._config: C = config

    @property
    def config(self) -> C:
        """
            Returns the configuration object of the current instance.

            This property provides access to the private `_config` attribute, which holds the
            configuration settings for this instance.

            Returns:
                C: The configuration object associated with the current instance.
        """
        return self._config

    @property
    def name(self) -> str:
        """
        Gets the name attribute of the object.

        This method serves as a property getter for the name attribute, providing
        external access to the internal `_name` attribute. The property is read-only.

        Returns:
            str: The name associated with the object.
        """
        return self._name

    @abstractmethod
    def process(self, item: I) -> Iterable[O]:
        """
        Processes an item and applies relevant facts to generate an output sequence. This
        method must be implemented by sub-classes as it is specific to each implementation.

        Args:
            item: Input element to be processed.

        Returns:
            Iterable of processed output elements generated from the input item and its
            associated facts.
        """

    def close(self) -> Iterable[O]:
        """
        Closes the current context, releasing any resources or finalizing any processing,
        and returns an iterable of results.

        This is typically used in contexts where a close operation aggregates or prepares
        data for a final output. The method should be called to ensure proper handling and
        cleanup of resources.

        Returns:
            Iterable[O]: An iterable containing the results collected or prepared during
            the close operation.
        """
        return tuple()

    @classmethod
    def _extract_item_type[T: Item](cls, item_type: type[T]) -> set[type[T]]:
        if isinstance(item_type, UnionType):
            return set(get_args(item_type))
        else:
            return {item_type}


    @classmethod
    def input_type(cls) -> set[type[I]]:
        """
        Returns the set of input types compatible with the `process` method of the class.

        The method inspects the type annotations for the parameter `item` in the
        signature of the `process` method. It extracts and processes the input types
        to ensure compatibility with the expected types for the method's operation.

        Returns:
            set[type[I]]: A set containing the extracted types for the `item` parameter
            within the `process` method.

        Raises:
            AttributeError: If the `process` method or annotations for `item` are not
            found within the class.

        """
        input_types: type[I] = signature(cls.process).parameters.get('item').annotation
        return cls._extract_item_type(input_types)


    @classmethod
    def output_type(cls) -> set[type[O]]:
        """
        Determines the output types of a subclass based on its `process` method's return annotation.

        This utility method analyzes the annotated return type of the `process` method
        to infer the types of outputs that the subclass is designed to produce. It is
        intended to facilitate type management and validation by extracting the return
        type from the function signature and provides this information in a standardized
        set format.

        Returns:
            set[type[O]]: A set containing the inferred output types from the annotated
            return type of the `process` method.
        """
        return cls._extract_item_type(signature(cls.process).return_annotation)

    @classmethod
    def config_type(cls) -> type[C]:
        """
        Returns the expected type of the 'config' parameter for the class.

        This method introspects the class's `__init__` method to retrieve the type
        annotation of the 'config' parameter. It can be used to enforce or verify
        type safety when instantiating objects of the class.

        Returns:
            type[C]: The annotated type of the 'config' parameter from the class's
                `__init__` method. If no annotation is provided for the 'config'
                parameter, this method will return `None`.
        """
        return signature(cls.__init__).parameters.get('config').annotation