from abc import ABC, abstractmethod
from collections.abc import Iterable

from bauklotz.reporting.fact import ItemFactStore
from bauklotz.reporting.item import Item
from bauklotz.reporting.report import Report, ReportConfiguration



class BufferedReport[I: Item, C: ReportConfiguration](Report[I, C], ABC):
    """
    BufferedReport class handles the storage of report entries in memory.

    This class extends Report and serves as an abstract base class (ABC) to
    manage buffered reporting functionality. It maintains a list of entries
    in memory, allowing them to be added via the `write` method. The entries
    can later be processed or stored persistently when the `close` method
    (to be implemented by subclasses) is called.

    Attributes:
        _entries (list[tuple[I, ItemFactStore]]): List of tuples where each
            tuple holds an item and associated ItemFactStore.
    """
    def __init__(self, name: str, config: C):
        """
        Initializes the object with the given name and configuration parameters and sets up
        an internal collection of entries.

        Args:
            name: str
                The name identifier for the object instance.
            config: C
                The configuration object providing initialization parameters.
        """
        super().__init__(name, config)
        self._entries: list[I] = list()

    def write(self, item: I) -> None:
        """
        Appends an item to the internal entries list.

        This method is used to add a single item to the list maintained
        internally by the instance. It does not perform validation or checks
        on the item being appended.

        Args:
            item (I): The item to append to the internal entries list.
        """
        self._entries.append(item)


    def _get_entries(self) -> Iterable[I]:
        """
        Fetch entries stored in the '_entries' attribute as an iterable sequence.

        This method retrieves all the items stored in the object's '_entries' attribute
        and yields them one by one, enabling iteration over the stored entries.

        Returns:
            Iterable[I]: An iterable sequence of items stored in the '_entries' attribute.
        """
        yield from self._entries

    @abstractmethod
    def close(self) -> None:
        """
        Closes the resource, ensuring any necessary cleanup operations are
        completed. This method is abstract and must be implemented by
        subclasses to provide the specific finalization or resource release
        logic.

        Raises:
            NotImplementedError: If the subclass does not implement this
                method.
        """