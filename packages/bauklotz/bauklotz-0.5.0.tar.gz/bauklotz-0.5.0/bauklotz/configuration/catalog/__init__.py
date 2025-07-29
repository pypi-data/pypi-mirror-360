from abc import ABC, abstractmethod

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.report import ReportConfiguration, Report


class FilterLocation(ABC):
    """
    An abstract base class that defines the interface for creating filter locations.

    The FilterLocation class is intended to be subclassed to define specific
    locations or mechanisms for filters to operate. It ensures that any subclass
    implements methods for retrieving a URI associated with the location and for
    creating filters based on a given name and configuration.

    Attributes:
        None
    """

    def __init__(self, uri: str, description: str | None):
        self._uri: str = uri
        self._description: str = description

    @property
    def description(self):
        """
        Gets the description attribute of the instance.

        Returns:
            str: The description stored in the '_description' attribute.
        """
        return self._description

    @property
    def uri(self) -> str:
        """
        Gets the URI associated with the object.

        The URI typically represents a unique identifier or a resource locator
        for the object. This property allows accessing the URI value.

        Returns:
            str: The URI of the object.
        """
        return self._uri

    @abstractmethod
    def create_filter(self, name: str, config: JSONType) -> Filter[Item, Item, FilterConfig]:
        """
        Creates and returns a filter based on the given name and configuration.

        This method serves as a factory function for creating filter instances. The
        specific type of filter created depends on the provided name and associated
        configuration. The returned filter is expected to process items of a given
        type (`Item`) and utilize configuration settings of type `FilterConfig`. It is
        an abstract method, meaning subclasses must implement their specific logic for
        creating and returning the appropriate filter.

        Args:
            name: A string representing the name of the filter to be created. This
                name determines the specific filter type to be instantiated.
            config: A dictionary-like JSON object representing the configuration
                settings for the filter. This configuration is utilized to customize
                the filter's behavior and operations.

        Returns:
            An instance of Filter that is parameterized to process `Item` objects as
            both input and output, with the configuration settings provided by
            `FilterConfig`.

        """


class ReportLocation:
    """
    Represents a location for creating reports.

    This class serves as a blueprint for defining report locations, including
    their URI and optional description. It provides methods to access the URI
    and description and includes an abstract method for creating reports.

    Attributes:
        _uri (str): The URI of the report location.
        _description (str | None): An optional description of the report location.
    """
    def __init__(self, uri: str, description: str | None):
        self._uri: str = uri
        self._description: str = description

    @property
    def description(self):
        """
        Returns the description of the object.

        This property retrieves the value of the private attribute `_description`.

        Returns:
            str: The description of the object.
        """
        return self._description

    @property
    def uri(self) -> str:
        """
        Represents a property that provides the value of the private '_uri' attribute.

        This property allows read-only access to the value stored in the '_uri'
        attribute. It retrieves the string that represents a Uniform Resource
        Identifier (URI) assigned to the object. URI is often used for identification
        or interaction between systems.

        Returns:
            str: The value of the '_uri' attribute.
        """
        return self._uri

    @abstractmethod
    def create_report(self, name: str, config: JSONType) -> Report[Item, ReportConfiguration]:
        """
        Generates a report based on the provided name and configuration.

        This method serves as an interface for creating a report. The report should
        be defined using the provided name and configuration details. Implementing
        classes must provide their own specific behavior for generating the report.

        Args:
            name: A string representing the unique name of the report to be created.
            config: A JSON structure containing configuration details required
                for generating the report.

        Returns:
            An instance of the Reporter class that is responsible for handling
            the generated report, implementing Item and ReportConfiguration as
            its generic parameters.
        """



class Catalog(ABC):
    """
    Represents an abstract catalog for managing filter and report locations.

    This class serves as an abstract base for managing filters and reports in a catalog
    implementation. Subclasses should implement the abstract methods to provide concrete
    behavior for managing `FilterLocation` and `ReportLocation` objects. Additionally, the
    class provides utility methods for creating filters and reports based on the stored
    locations.

    Attributes:
        None
    """
    @abstractmethod
    def add_location(self, location: FilterLocation | ReportLocation) -> None:
        """
        Represents an abstract base class that defines a method for adding a location
        to a filter. This class is intended to be subclassed, and concrete
        implementations should provide their own logic for adding locations.

        Methods:
            add_location: Abstract method to add a location to the filter.
        """

    @abstractmethod
    def get_location(self, uri: str) -> FilterLocation | ReportLocation:
        """
        Defines an abstract method for obtaining the location of a filter based on
        a provided URI.

        Args:
            uri: The URI string that will be used to determine the filter location.

        Returns:
            FilterLocation: An instance representing the location derived from the
            provided URI.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """

    def build_filter(self, filter_uri: str, name: str, config: JSONType) -> Filter[Item, Item, FilterConfig]:
        return self.get_location(filter_uri).create_filter(name, config)

    def build_report(self, report_uri: str, name: str, config: JSONType) -> Report[Item, ReportConfiguration]:
        return self.get_location(report_uri).create_report(name, config)

    @abstractmethod
    def get_filters(self) -> set[FilterLocation]:
        """
        Defines the interface for retrieving filter locations, which must be implemented by
        any subclass. Classes inheriting from the base class should provide their own
        implementation for retrieving a set of `FilterLocation` objects.

        Returns:
            set[FilterLocation]: A set containing the filter locations.
        """

    @abstractmethod
    def get_reports(self) -> set[ReportLocation]:
        """
        Defines an abstract method that, when implemented, should return a collection of report
        locations.

        Methods:
            get_reports: Abstract method to be implemented by subclasses, returning a set
            of report locations.

        Returns:
            set[ReportLocation]: A set of ReportLocation objects.
        """