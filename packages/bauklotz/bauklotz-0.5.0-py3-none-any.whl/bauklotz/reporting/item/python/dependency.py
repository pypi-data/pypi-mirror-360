from stdlib_list import stdlib_list

from bauklotz.reporting.item.dependency import ImportDependency
from bauklotz.reporting.item.python.project import PythonSourceFile

IMPORT_3RD_PARTY: str = '3rd party'
IMPORT_STDLIB: str = 'stdlib'
IMPORT_PROJECT: str = 'project'

class PythonImport(ImportDependency[PythonSourceFile]):
    """
    Represents a Python import dependency within a source file.

    This class is used to analyze and classify dependencies in a Python source
    file. It identifies modules and symbols imported by the source file, determines
    the category of the import (e.g., standard library, third-party, or project
    imports), and links dependency relations between source files.

    Attributes:
        dependant (PythonSourceFile): The source file that contains the dependency.
        depends_on_module (str): The module on which the source file depends.
        imported_names (dict[str, str | None]): A mapping of imported names from the
            module and their aliases or `None` if no alias is used.
    """
    def __init__(self, dependant: PythonSourceFile, depends_on_module: str, imported_names: dict[str, str | None]):
        super().__init__(dependant, depends_on_module, imported_names)

    @property
    def id(self) -> str:
        return self._dependant.module_name

    def import_category(self) -> dict[str, str]:
        """
        Determines the category of each imported artifact based on dependency context.

        This function categorizes the imported artifacts as either standard library,
        third-party, or project imports. The categorization is based on the Python
        version, standard library modules, and the dependency source of the
        current context.

        Returns:
            dict[str, str]: A dictionary where the keys are the names of the
            imported artifacts, and the values are their respective categories
            (`IMPORT_STDLIB`, `IMPORT_3RD_PARTY`, or `IMPORT_PROJECT`).

        Raises:
            None

        """
        major, minor, _ = self._dependant.python_version
        stdlib: set[str] = set(stdlib_list(f"{major}.{minor}"))
        base_module: str = self._dependency_source.split('.')[0]
        category: str = IMPORT_3RD_PARTY
        if base_module in stdlib:
            category = IMPORT_STDLIB
        if self._dependant.canonical_id.startswith(base_module):
            category = IMPORT_PROJECT
        return dict(
            (name, category)
            for name in self.imported_artifacts
        )
