from collections.abc import Iterable
from importlib.util import find_spec
from itertools import chain
from pathlib import Path
from pkgutil import walk_packages

from bauklotz.configuration.catalog.plugin import ContribCatalog

_FILTER_PACKAGE: str = 'bauklotz.business.filter'
_REPORT_PACKAGE: str = 'bauklotz.reporting.report'

class BuiltinCatalog(ContribCatalog):
    def __init__(self, contrib_modules: Iterable[str] = tuple()):
        super().__init__(chain(self._get_builtin_packages(), contrib_modules))
        self._filters = dict(
            (f'builtin{uri.removeprefix(_FILTER_PACKAGE)}', location)
            for uri, location in self._filters.items()
        )
        self._reports = dict(
            (f'builtin{uri.removeprefix(_REPORT_PACKAGE)}', location)
            for uri, location in self._reports.items()
        )

    @staticmethod
    def _get_builtin_packages() -> Iterable[str]:
        for location in ('bauklotz.reporting.report', 'bauklotz.business.filter'):
            base: str | None = find_spec(location).origin
            if not base:
                raise ImportError(f'Could not find {location} package')
            else:
                for finder, name, is_pkg in walk_packages([str(Path(base).parent)], f'{location}.'):
                    if not is_pkg:
                        yield name
