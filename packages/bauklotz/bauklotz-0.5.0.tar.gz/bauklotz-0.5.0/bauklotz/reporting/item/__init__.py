from abc import ABC, abstractmethod
from collections.abc import Iterator
from copy import deepcopy
from typing import Self

from bauklotz.reporting.fact import ItemFactStore
from bauklotz.reporting.types import JSONType


class Label:
    def __init__(self, labels: set[str] | None = None):
        self._labels = set(map(str.lower, labels or set()))

    def set_from(self, labels: set[str] | Self) -> Self:
        self._labels = set(map(str.lower, labels))
        return self

    def __add__(self, other) -> 'Label':
        if isinstance(other, str):
            result: Label = Label(self._labels)
            result._labels.add(other.lower())
            return result
        else:
            raise TypeError(f'unsupported operand type(s) for +: \'{type(self).__name__}\' and \'{type(other).__name__}\'')

    def __sub__(self, other) -> Self:
        if isinstance(other, str):
            result: Label = Label(self._labels)
            result._labels.discard(other.lower())
            return result
        else:
            raise TypeError(f'unsupported operand type(s) for +: \'{type(self).__name__}\' and \'{type(other).__name__}\'')

    def __iadd__(self, label: str) -> Self:
        self._labels.add(label.lower())
        return self

    def __isub__(self, label: str) -> Self:
        self._labels.discard(label.lower())
        return self

    def __contains__(self, item: str):
        return item.lower() in self._labels

    def __iter__(self) -> Iterator[str]:
        return iter(self._labels)

    def __bool__(self) -> bool:
        return bool(self._labels)

    def __str__(self) -> str:
        ls: str = ', '.join(sorted(self._labels))
        return f'{{{ls}}}'

class Item(ABC):
    """
    Abstract base class that serves as a blueprint for objects with cloning and
    serialization functionality.

    This class provides a default implementation for cloning an object and
    requires subclasses to implement a method for serializing the object into
    a JSON-compatible format. Subclasses can extend the functionality to meet
    specific requirements for their use case.

    Attributes:
        None
    """
    def __init__(self):
        self._labels: Label = Label()
        self._facts: ItemFactStore = ItemFactStore()


    @property
    def facts(self) -> ItemFactStore:
        return self._facts


    @property
    def labels(self) -> Label:
        """
        Gets the set of labels associated with the instance.

        The property retrieves a set of labels stored in the internal
        private attribute `_labels`.

        Returns:
            set[str]: A set containing all labels for the instance.
        """
        return self._labels

    @labels.setter
    def labels(self, labels: Label) -> None:
        self._labels = labels


    def clone(self) -> Self:
        """
        Creates and returns a deep copy of the current object.

        This method generates an independent copy of the current object by leveraging
        the `deepcopy` function from Python's `copy` module. The returned copy will
        have the same data as the original but will not share references with it, ensuring
        modifications to the copy have no impact on the original object.

        Returns:
            Self: A deep copy of the current object.
        """
        return deepcopy(self)

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Represents an abstract property 'id' that must be implemented by any concrete class that inherits
        from the class defining this abstract property. This property is expected to return a string value
        representing a unique identifier or specific characteristic.

        Returns:
            str: A unique identifier or specific characteristic of the derived class instance.
        """

    @property
    def canonical_id(self) -> str:
        """
        Returns the canonical identifier for the instance.

        The canonical identifier is constructed using the object's `id` and the name of its
        class, separated by an '@' symbol.

        Returns:
            str: A string representing the canonical identifier of the instance.
        """
        return f'{self.id}@{self.__class__.__name__}'

    @abstractmethod
    def serialize(self) -> JSONType:
        """
        Defines an abstract method for serializing an object into a JSON-compatible format.

        This method should be implemented by subclasses to provide a mechanism for
        converting an object instance into a format that is compatible with JSON
        serialization. The implementation must return a structured data type such as
        a dictionary, list, or scalar value representing the serialized state of the
        object.

        Returns:
            JSONType: A dictionary, list, scalar, or other JSON-compatible data type
            that represents the serialized object.
        """

    def __hash__(self) -> int:
        return hash(self.canonical_id)