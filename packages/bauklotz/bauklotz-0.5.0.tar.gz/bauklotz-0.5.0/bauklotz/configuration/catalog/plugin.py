from collections.abc import Iterable
from importlib import import_module

from bauklotz.business.filter import Filter, FilterConfig
from bauklotz.configuration.catalog import FilterLocation, Catalog, ReportLocation
from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.report import Report, ReportConfiguration


class ModuleFilterLocation(FilterLocation):
    """
    Represents a filter location within a module.

    This class is used to locate and load filter classes from specified Python
    modules dynamically. It locates a filter class based on a string URI, verifies
    its type, and initializes it for further usage. The primary purpose is to
    provide a mechanism to dynamically create and configure filters based on their
    deserialized configuration.

    Attributes:
        _filter (type[Filter]): The filter class dynamically located and verified
            based on the given URI. Only subclasses of the `Filter` class are
            considered valid.
    """
    def __init__(self, uri: str):
        module_name, attr_name = uri.rsplit(".", 1)
        module = import_module(module_name)
        element = getattr(module, attr_name)
        if not isinstance(element, type) or not issubclass(element, Filter):
            raise TypeError(f"{element} is not a subclass of Filter")
        else:
            self._filter: type[Filter] = element
        super().__init__(f'{module_name}:{attr_name}', self._filter.__doc__)


    def create_filter(self, name: str, config: JSONType) -> Filter[Item, Item, FilterConfig]:
        return self._filter(name, self._filter.config_type().deserialize(config))


class ModuleReportLocation(ReportLocation):
    def __init__(self, uri: str):
        module_name, attr_name = uri.rsplit(".", 1)
        module = import_module(module_name)
        element = getattr(module, attr_name)
        if not isinstance(element, type) or not issubclass(element, Report):
            raise TypeError(f"{element} is not a subclass of Reporter")
        else:
            self._reporter: type[Report] = element
        super().__init__(f'{module_name}:{attr_name}', self._reporter.__doc__)

    def create_report(self, name: str, config: JSONType) -> Report[Item, ReportConfiguration]:
        return self._reporter(name, self._reporter.config_type().deserialize(config))



class ContribCatalog(Catalog):
    """Class for managing and organizing contributed filter modules.

    This class is designed to handle contributed modules containing filters, allowing
    for discovery, organization, and retrieval of filter locations. It enables the integration
    of external filter modules into the application.

    Attributes:
        _filters (dict[str, FilterLocation]): Internal storage for filter locations organized
            by their URI.
    """
    def __init__(self, contrib_modules: Iterable[str] | str):
        contrib_modules = [contrib_modules] if isinstance(contrib_modules, str) else tuple(contrib_modules)
        self._filters: dict[str, FilterLocation] = dict()
        self._reports: dict[str, ReportLocation] = dict()
        for module in contrib_modules:
            for location in self._discover_filters(module):
                self._filters[location.uri] = location
        for module in contrib_modules:
            for location in self._discover_reports(module):
                self._reports[location.uri] = location


    def add_location(self, location: FilterLocation | ReportLocation) -> None:
        if isinstance(location, ReportLocation):
            self._reports[location.uri] = location
        else:
            self._filters[location.uri] = location

    def get_location(self, uri: str) -> FilterLocation | ReportLocation:
        return self._reports[uri] if uri in self._reports else self._filters[uri]

    def get_filters(self) -> set[FilterLocation]:
        return set(self._filters.values())

    def get_reports(self) -> set[ReportLocation]:
        return set(self._reports.values())

    @staticmethod
    def _discover_filters(module_name: str) -> Iterable[FilterLocation]:
        module = import_module(module_name)
        for attr_name in dir(module):
            if isinstance(element := getattr(module, attr_name), type) and issubclass(element, Filter):
                yield ModuleFilterLocation(f'{module_name}.{attr_name}')

    @staticmethod
    def _discover_reports(module_name: str) -> Iterable[ReportLocation]:
        module = import_module(module_name)
        for attr_name in dir(module):
            if isinstance(element := getattr(module, attr_name), type) and issubclass(element, Report):
                yield ModuleReportLocation(f'{module_name}.{attr_name}')