from abc import abstractmethod
from collections.abc import Sequence, Iterable
from enum import Enum
from pathlib import Path
from typing import ClassVar

from toolz import drop

from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.graph import Graph, GraphType, GraphNode


class ProjectFile(Item):
    """
    Represents a project file with functionality to extract its metadata.

    This class provides a representation of a file object, encapsulating its path
    and providing access to its name and parent directories. It is intended to
    work with file paths and facilitate operations related to the file's structure.

    Attributes:
        _file_path (Path): The complete path of the file as a Path object.
    """

    def __init__(self, file_path: Path, base_path: Path):
        self._base_dir: Path = base_path
        self._file_path: Path = file_path.relative_to(base_path)
        self._absolute_path: Path = file_path.absolute()
        super().__init__()

    def __hash__(self):
        return hash(self._file_path)

    @property
    def canonical_id(self) -> str:
        """
        Returns the canonical identifier of the file.

        The canonical identifier is represented as a string version of the file
        path associated with this object.

        Returns:
            str: The canonical identifier derived from the file path.
        """
        return str(self._file_path)

    @property
    def id(self) -> str:
        return self._absolute_path.as_uri()


    @property
    def path(self) -> Path:
        """
        Provides a property to retrieve the file path associated with the object.

        Attributes:
            _file_path (Path): The internal file path stored in the object.

        Returns:
            Path: The file path associated with the object.
        """
        return self._absolute_path

    @property
    def base_dir(self) -> Path:
        """
        Returns the base directory path associated with the instance.

        This is a property that provides read access to the private `_base_dir`
        attribute, which typically represents the base directory used or
        configured within the instance.

        Returns:
            Path: The base directory path.
        """
        return self._base_dir

    @property
    def content(self) -> str:
        with self._absolute_path.open() as src:
            return src.read()

    @property
    def project_relative_path(self) -> Path:
        """
        Retrieves the project-relative file path.

        This property returns the file path relative to the project. It ensures that
        the stored path is encapsulated and programmatically accessed.

        Returns:
            Path: The path relative to the project.
        """
        return self._file_path

    @property
    def file_name(self) -> str:
        """
        Returns the name of the file.

        This property extracts and returns the name of the file from the file path
        stored in the `_file_path` attribute.

        Returns:
            str: The name of the file as a string.
        """
        return self._file_path.name

    @property
    def parents(self) -> Sequence[Path]:
        """
        Gets the parent directories of the current file path.

        This property returns all parent directories of the file path as a sequence of
        Path objects, ordered from the immediate parent to the root directory.

        Returns:
            Sequence[Path]: A sequence containing the parent directories of the file path.
        """
        return tuple(drop(1, reversed(self._file_path.parents)))

    def serialize(self) -> JSONType:
        return str(self._file_path)


class ProjectLocation(Item):
    """
    Represents a project's location and provides functionality to interact with it.

    This class encapsulates the path of a project directory and offers methods to
    retrieve the project name, list files in the directory, determine file validity,
    and serialize the project's path for JSON-compatible operations. It serves as
    an abstraction for interacting with files and directories within a project.

    Attributes:
        _project_path (Path): The root path of the project directory.
    """
    def __init__(self, project_path: Path):
        self._project_path: Path = project_path
        super().__init__()

    @property
    def id(self) -> str:
        return self._project_path.absolute().as_uri()

    @property
    def project_name(self) -> str:
        """
        Returns the name of the project derived from the project path.

        The property retrieves the last component of the path (interpreted as the
        project name) from the `_project_path` attribute.

        Returns:
            str: The name of the project.
        """
        return self._project_path.name

    def files(self) -> Iterable[ProjectFile]:
        """
        Yields project files located in the project directory.

        This generator function recursively walks through the directory structure
        starting from the project's root directory and yields all files as instances
        of `ProjectFile`. The relative paths of the files are calculated with respect
        to the parent of the root project directory.

        Returns:
            Iterable[ProjectFile]: Yields `ProjectFile` objects representing the
            relative paths of files in the project directory.
        """
        for current_dir, _, files in self._project_path.walk():
            if self._is_hidden_dir(current_dir):
                continue
            for file in files:
                file_path: Path = current_dir.joinpath(file)
                if self._is_project_file(current_dir.joinpath(file)):
                    yield ProjectFile(file_path, self._project_path)

    @staticmethod
    def _is_hidden_dir(directory: Path) -> bool:
        return any(map(lambda p: p.startswith('.'), directory.parts))

    def _is_project_file(self, file_path: Path) -> bool:
        """
        Checks if the provided file path corresponds to a valid project file.

        This method evaluates the given file path and determines whether it meets
        the criteria for being considered a project file.

        Args:
            file_path (Path): The path to the file that needs to be checked.

        Returns:
            bool: True if the file path corresponds to a project file, otherwise False.
        """
        return True

    def serialize(self) -> JSONType:
        """
        Serializes the object's project path to a JSON-compatible representation.

        The method retrieves the internal `_project_path` attribute and converts
        it into a string format that can be used in JSON-compatible operations.

        Returns:
            JSONType: A JSON-compatible string form of the `_project_path`.
        """
        return str(self._project_path)


class FileNode(GraphNode):
    def __init__(self, path: Path, file_type: str = 'File', **attributes: JSONType):
        super().__init__(path.absolute().as_uri(), path.name, file_type, **attributes)

class DirectoryNode(GraphNode):
    NODE_TYPE: ClassVar[str] = 'Directory'
    def __init__(self, path: Path):
        super().__init__(path.absolute().as_uri(), path.name, self.NODE_TYPE)


class ProjectNode(GraphNode):
    NODE_TYPE: ClassVar[str] = 'Project'
    def __init__(self, project_name: str):
        super().__init__(f'{project_name}@project', project_name, self.NODE_TYPE)


class ProjectGraph(Graph):
    def __init__(self, project_name: str):
        super().__init__(GraphType.DIRECTED)
        self._project_node: ProjectNode = ProjectNode(project_name)
        self.add_node(self._project_node)
        self._project_name: str = project_name

    @property
    def id(self) -> str:
        return self._project_name

    def add_file(self, file: ProjectFile, file_type: str = 'File', attributes: dict[str, JSONType] | None = None):
        """
        Adds a file to the project structure, including all necessary parent directories. Each parent directory is added
        recursively, connected to its parent node, until the specified file's node is created and connected.

        Args:
            file (ProjectFile): The file to be added, including its path and associated parent directories.
            file_type (str, optional): The type of the file. Default is 'File'.
        """
        last_node: GraphNode = self._project_node
        for parent in file.parents:
            dir_node: DirectoryNode = DirectoryNode(parent)
            if dir_node.id not in self._graph.nodes:
                self.add_node(dir_node)
                self.connect_nodes(last_node.id, dir_node.id)
            last_node = dir_node
        file_node: FileNode = FileNode(file.path, file_type, **(attributes or {}))
        self.add_node(file_node)
        self.connect_nodes(last_node.id, file_node.id)

