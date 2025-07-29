from bauklotz.reporting.item import Item
from bauklotz.reporting.item.project import ProjectFile


class ImportDependency[F: ProjectFile](Item):
    """
    Represents an import dependency between a dependant and dependency source.

    This class models the relationship of a `dependant` with a `dependency_source`,
    including all artifacts imported from the dependency source. It provides
    capabilities for extracting metadata about the dependency relationship,
    such as unique identifiers, imported artifacts, their respective weights, and
    categories. Additionally, it offers serialization utilities for downstream
    consumption.

    Attributes:
        _dependant (F): The dependant consuming the dependency source.
        _dependency_source (str): The source of the dependency being imported.
        _imported_artifacts (dict[str, str]): A mapping of artifact names to their
            alternate aliases if provided, defaulting to artifact names themselves.
    """
    def __init__(self, dependant: F, dependency_source: str, imported_artifacts: dict[str, str | None]):
        """
        Initializes an instance of the class, and sets up internal attributes related to
        the dependant object, the source of dependencies, and the mapping of imported
        artifacts.

        Args:
            dependant: Callable or function serving as the dependant, which can include
                logic that relies on external dependencies.
            dependency_source: String representing the source or context of dependencies,
                e.g., a file path, module, or other source identifier.
            imported_artifacts: Dictionary mapping the names of imported artifacts (keys)
                to their aliases (values). If no alias is specified, the artifact name is
                used as the alias.

        Attributes:
            _dependant: Stores the dependant function or callable provided during
                initialization.
            _dependency_source: Stores a string identifier for the source of dependencies.
            _imported_artifacts: A dictionary where keys are artifact names and values are
                aliases. If no alias is provided during initialization, the artifact name
                is used as the alias.
        """
        self._dependant: F = dependant
        self._dependency_source: str = dependency_source
        self._imported_artifacts: dict[str, str] = dict(
            (artifact, alias or artifact)
            for artifact, alias in imported_artifacts.items()
        )
        super().__init__()

    @property
    def dependant(self) -> F:
        return self._dependant

    @property
    def id(self) -> str:
        return f'{self._dependant.canonical_id} -> {self._dependency_source}'

    @property
    def dependency_id(self) -> str:
        """
        Returns the dependency ID of the current instance.

        This property provides a way to retrieve the dependency ID stored in
        the `_dependency_source` attribute. The dependency ID is typically
        used to uniquely identify or track a specific dependency source
        within a system or application context.

        Returns:
            str: The unique identifier of the dependency source.
        """
        return self._dependency_source

    @property
    def imported_artifacts(self) -> set[str]:
        """
        Returns the set of imported artifacts.

        This property provides access to the set of all artifacts that have been
        imported. It retrieves this information from an internal attribute and
        presents it as a Python set.

        Attributes:
            imported_artifacts (set[str]): A set containing the names of imported
                artifacts.
        """
        return set(self._imported_artifacts)

    def weight_imports(self) -> dict[str, int]:
        """
        Calculates the weight of imported artifacts.

        This method iterates through the list of imported artifacts and assigns a
        static weight of 1 to each artifact. The output is a dictionary where the
        keys represent the artifacts and the values represent their respective
        weights.

        Returns:
            dict[str, int]: A dictionary mapping each imported artifact to its
            assigned weight.
        """
        return dict((artifact, 1) for artifact in self.imported_artifacts)

    def import_category(self) -> dict[str, str]:
        """
        Converts a list of imported artifacts to a dictionary with default category.

        The method processes the imported artifacts stored in the `imported_artifacts`
        attribute and converts them into a dictionary where each key represents
        an artifact name, and the value is a string indicating the category, set to
        'default' for all artifacts.

        Returns:
            dict[str, str]: A dictionary mapping artifact names to the default
            category ('default').
        """
        return dict((artifact, 'default') for artifact in self.imported_artifacts)


    def serialize(self) -> dict[str, str]:
        """
        Serializes the object's attributes into a dictionary representation.

        Returns:
            dict[str, str]: A dictionary containing the serialized attributes of the object,
            including 'dependant' as the canonical ID of the dependant property,
            'dependency_source' as the dependency source string, and
            'imported_artifacts' as the imported artifacts details.
        """
        return {
            'dependant': self._dependant.canonical_id,
            'dependency_source': self._dependency_source,
            'imported_artifacts': self._imported_artifacts
        }