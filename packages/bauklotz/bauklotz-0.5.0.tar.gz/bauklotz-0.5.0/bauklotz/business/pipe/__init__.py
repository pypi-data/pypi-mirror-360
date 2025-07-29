from abc import ABC, abstractmethod
from typing import Any

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.reporting.item import Item
from bauklotz.reporting.logging import BauklotzLogger, NoopLogger
from bauklotz.reporting.report import Report, ReportConfiguration


class Pipe(ABC):
    """
    Defines the interface and operations for constructing a data processing pipeline.

    This abstract base class provides the necessary methods to construct, configure,
    and manage a pipeline for processing data items. It enforces a contract for
    injecting items, managing channels and filters, and generating reports. Each
    subclass must implement the provided abstract methods to define its specific
    behavior and processing logic.

    Attributes:
        None
    """

    def __init__(self, logger: BauklotzLogger | None = None):
        self._logger = logger or NoopLogger()

    @abstractmethod
    def inject(self, item: Item, channel: str) -> None:
        """
        Abstract method for injecting an item into a specified channel. This method must
        be implemented by subclasses to define how an `Item` should interact with a
        particular channel.

        Args:
            item (Item): The item to be injected.
            channel (str): The destination channel where the item will be injected.

        Returns:
            None
        """


    @abstractmethod
    def close(self) -> None:
        """
        Represents an abstract method for closing resources or performing cleanup.

        This method must be implemented by subclasses to ensure specific
        resources used by the subclass are properly managed and released.

        Raises:
            NotImplementedError: If the method is not overridden in the subclass.
        """

    @abstractmethod
    def add_input_channel(self, name: str) -> None:
        """
        Adds an input channel by the specified name.

        This method is an abstract method, intended to be implemented in subclasses. It will define
        the logic to add an input channel to the respective system. Each implementation should specify
        how the input channel is processed or stored.

        Args:
            name: The name of the input channel to be added.
        """

    @abstractmethod
    def add_filter(self, filter_: Filter[Item, Item, FilterConfig]) -> None:
        """
        Adds a filter to the current instance which will process items based on the defined
        filter logic. The filter modifies or filters the items according to the configuration
        provided.

        Args:
            filter_: A filter instance that determines how items are processed or filtered.
        """


    @abstractmethod
    def add_report(self, report: Report[Item, ReportConfiguration]) -> None:
        """
        Adds a report to the system.

        This method should be overridden by subclasses to define how a report is added
        to the specific implementation of the system.

        Args:
            report: The report to be added, which contains details of type Report[Item].

        """

    @abstractmethod
    def connect[I: Item](
            self,
            filter_: Filter[Item, I, FilterConfig],
            end: Report[I, ReportConfiguration] | Filter[I, Item, FilterConfig],
            labels: set[str] | None = None
    ) -> None:
        """
        Connects an item with a specified filter and an endpoint that can be either a
        report or another filter. This method should be implemented by subclasses to
        define how the connection is established.

        Args:
            filter_:
                The filter to process items, defined by types `Filter[Item, I, FilterConfig]`.
            end:
                The endpoint to connect to, which can be either a report of type
                `Report[I]` or another filter of type `Filter[I, Item, FilterConfig]`.
        """

    @abstractmethod
    def wire(self, channel_name: str, filter_: Filter[Item, Item, FilterConfig]) -> None:
        """
        Wires a channel to a specified filter to process items according to the filter's configuration.
        This method establishes the relationship necessary for data to flow through the filter.

        Args:
            channel_name: Name of the channel to be wired.
            filter_: Filter instance responsible for processing data for the specified channel.
        """

    def visualize(self, filename: str) -> str:
        """
        Visualizes the current state or output of the process implemented in the pipe.

        The visualization mechanism is dependent on the specific implementation of the
        pipe. Each subclass should provide its own implementation if applicable. For
        pipes that do not support visualization, this method will raise a
        NotImplementedError.

        Args:
            filename: The name of the file in which the visualization should be saved.

        Returns:
            The file path where the visualization output is stored.

        Raises:
            NotImplementedError: If the pipe does not support visualization.
        """
        raise NotImplementedError('Pipe does not support visualization.')
