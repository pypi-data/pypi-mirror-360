from collections.abc import Iterable, Iterator
from operator import attrgetter

from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.project import ProjectFile

class Module[_F: ProjectFile](Item):
    """
    Represents a module in the project which contains a collection of defined files.

    This class encapsulates the concept of a module, characterized by its name and
    associated files. It allows for adding files to the module, iterating over its
    contents, and serializing its data for storage or transmission.

    Attributes:
        _name (str): The name of the module.
        _defined_in (set[_F]): A collection of files associated with the module,
            where _F is a generic type representing a specific file type.
    """
    def __init__(self, name: str, defined_in: Iterable[_F]):
        """
        Represents an instance with a name and a set of definitions. This class allows
        initializing an instance using a name string and iterable of definitions, which
        are stored as a set.

        Attributes:
            _name: The name of the instance.
            _defined_in: A set containing the definitions associated with the instance.

        Args:
            name: A string representing the name of the instance.
            defined_in: An iterable containing definitions associated with the instance.
        """
        super().__init__()
        self._name = name
        self._defined_in: set[_F] = set(defined_in)

    @property
    def id(self) -> str:
        return self._name

    def add_file(self, file: _F):
        """
        Adds a file to the internal set of defined files.

        This method is used to register a file into the `_defined_in` set, ensuring
        that it is tracked internally.

        Args:
            file (_F): The file to be added to the `_defined_in` set, ensuring it is
            uniquely registered within the instance.
        """
        self._defined_in.add(file)

    def __iter__(self) -> Iterator[_F]:
        """
        Creates an iterator for the `_defined_in` attribute of the object, allowing
        the object to be iterated over. This method provides a mechanism to return
        an iterator over the object's contained elements.

        Returns:
            Iterator[_F]: An iterator over the elements stored in `_defined_in`.
        """
        return iter(self._defined_in)

    def serialize(self) -> JSONType:
        """
        Serializes the current instance into a JSON-compatible format.

        The method converts the instance's attributes into a dictionary format
        that can be used for JSON serialization. Specifically, it includes the
        `name` attribute and a sorted list of canonical IDs derived from the
        `defined_in` attribute. The canonical IDs are obtained using the
        `attrgetter` utility.

        Returns:
            JSONType: A dictionary with the serialized attributes: `name` as a
            string and `defined_in` as a sorted list of strings representing
            canonical IDs of the associated objects.
        """
        return dict(name=self._name, defined_in=sorted(map(attrgetter('canonical_id'), self._defined_in)))



class Component[_M: Module](Item):
    """
    Represents a component with a type, name, and associated modules.

    This class is a generic representation of a component. It allows defining a specific
    type and name for the component. The component can be associated with a set of modules.
    Each module added to the component should adhere to the constraints of the generic type.

    Attributes:
        _component_type (str): Capitalized type of the component.
        _name (str): Name of the component.
        _modules (set[_M]): Set of modules associated with the component, where _M is a
            type that extends Module.
    """
    def __init__(self, component_type: str, name: str, modules: Iterable[_M] = tuple()):
        """
        Initializes an instance of the class with a component type, name, and an optional set of
        modules.

        Args:
            component_type: The type of the component. Will be capitalized automatically.
            name: The name of the component.
            modules: An optional iterable of modules associated with the component. Defaults to an
                empty tuple.
        """
        super().__init__()
        self._component_type: str = component_type.capitalize()
        self._name: str = name
        self._modules: set[_M] = set(modules)

    @property
    def id(self) -> str:
        return f'{self._name}@{self._component_type}'

    def add_module(self, module: _M):
        """
        Adds a module to the internal module set.

        This method allows adding a new module to the existing collection
        of modules maintained by the instance. The module is stored in a
        set, ensuring no duplicate entries. This method modifies the internal
        state of the instance by updating the module set.

        Args:
            module: The module to be added. The module should be an instance of
                the specified type `_M` and will be included in the managed set
                if it is not already present.

        """
        self._modules.add(module)

    def serialize(self) -> JSONType:
        """
        Serializes the object's attributes into a dictionary format.

        This method collects the relevant attributes of the object, including its name,
        type, and a list of associated modules (sorted by their canonical IDs), and
        formats them into a dictionary structure for easy JSON serialization or data
        transfer.

        Returns:
            JSONType: A dictionary containing the serialized attributes of the object.
        """
        return dict(
            name=self._name,
            component_type=self._component_type,
            modules=sorted(map(attrgetter('canonical_id'), self._modules))
        )
