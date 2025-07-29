from typing import Self, Iterable

from bauklotz.business.filter import Filter, FilterConfig
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.python.project import PythonProjectLocation, PythonSourceFile, PythonProjectGraph


class PythonProjectConfig(FilterConfig):
    """
    Represents the configuration for a Python project with control over special file handling.

    This class stores configuration settings used to filter or process files specific to
    a Python project. It allows for serialization and deserialization from a JSON-like
    object for persistence or interoperability. It also provides a property to access
    whether special files should be ignored during processing.

    Attributes:
        _ignore_special_files (bool): Specifies if special files are to be ignored.
    """
    def __init__(self, ignore_special_files: bool = False):
        self._ignore_special_files: bool = ignore_special_files

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        """
        Deserializes a JSON object into an instance of the class.

        This method serves to reconstruct an object of the class from a JSON-compatible
        dictionary. It accesses the relevant key-value pair to initialize the corresponding
        attribute of the class instance.

        Args:
            data: JSONType. A dictionary-like object containing the serialized
                representation of the class instance.

        Returns:
            Self. A new instance of the class initialized with data from the provided
            JSON dictionary.
        """
        return cls(data.get('ignore_special_files', False))

    @property
    def ignore_special_files(self):
        """
        Property to get the value of the '_ignore_special_files' attribute.

        This property allows access to the private '_ignore_special_files' attribute,
        indicating whether special files should be ignored in some internal processing
        logic. The return value directly reflects the state of the attribute and is a
        boolean.

        Returns:
            bool: The value of the '_ignore_special_files' attribute.
        """
        return self._ignore_special_files


class PythonProjectFilter(Filter[PythonProjectLocation, PythonSourceFile, PythonProjectConfig]):
    """
    Represents a filter for processing Python projects.

    This class filters Python source files within a project location based on
    specific criteria defined in the project configuration. Its primary purpose
    is to traverse a Python project, analyze its files, and yield only those
    files that meet the filter's conditions.

    Attributes:
        name (str): The name of the filter.
        config (PythonProjectConfig): Configuration settings for how the filter processes files, including any specific
        rules for ignoring certain files.
    """
    def __init__(self, name: str, config: PythonProjectConfig):
        super().__init__(name, config)


    def process(self, item: PythonProjectLocation) -> Iterable[PythonSourceFile]:
        """
        Processes the given item, filtering and yielding Python source files based on specific
        conditions, such as the file name prefix and configuration settings.

        Args:
            item: The Python project location containing files to process.

        Yields:
            PythonSourceFile: Each eligible Python source file from the input item.
        """
        for file in item.files():
            if file.file_name.startswith('__') and self.config.ignore_special_files:
                continue
            yield file



class PythonProjectGraphConfig(FilterConfig):
    def __init__(self, project_name: str = 'Project'):
        self.project_name: str = project_name

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data.get('project_name', 'Project'))


class PythonProjectGraphFilter(Filter[PythonSourceFile, PythonProjectGraph, PythonProjectGraphConfig]):
    def __init__(self, name: str, config: PythonProjectGraphConfig):
        super().__init__(name, config)
        self._project_fileset: set[PythonSourceFile] = set()

    def process(self, item: PythonSourceFile) -> Iterable[PythonProjectGraph]:
        self._project_fileset.add(item)
        return ()

    def close(self) -> Iterable[PythonProjectGraph]:
        project_graph: PythonProjectGraph = PythonProjectGraph(self.config.project_name)
        for file in self._project_fileset:
            project_graph.add_file(file, 'Python File', dict(file.facts.items()))
        self._project_fileset.clear()
        yield project_graph