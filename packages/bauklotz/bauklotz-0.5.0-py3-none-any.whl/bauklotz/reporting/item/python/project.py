from ast import parse, Module, walk, Import, ImportFrom
from collections.abc import Iterable
from pathlib import Path
from sys import stderr
from tomllib import load
from typing import Protocol

from toolz import get_in

from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.project import ProjectLocation, ProjectFile, ProjectGraph


class InvalidPythonProject(LookupError):
    """
    Represents an error when a Python project is invalid.

    This exception is raised to signify problems with the validity or structure of
    a Python project. It extends the standard `LookupError` to provide a more
    specific error subclass for issues related to Python project validation.
    """
    pass



class PyProjectFile:
    """
    Represents a Python project file, providing access to its metadata.

    This class processes a configuration file (e.g., pyproject.toml) and allows
    retrieval of specific metadata, such as the project's name. It is intended
    to support tools or scripts that interact with project configuration files.

    Attributes:
        _path (Path): The file path to the project configuration file.
        _data (dict[str, JSONType]): Parsed configuration data from the file.
    """
    def __init__(self, path: Path):
        self._path: Path = path
        with self._path.open('rb') as src:
            self._data: dict[str, JSONType] = load(src)

    @property
    def name(self) -> str:
        """
        Gets the name of the project defined in the configuration.

        The property retrieves the 'name' field under the 'tool.poetry' section
        from the provided configuration data. If the name is not defined, it
        returns None.

        Returns:
            str: The project name if defined in the configuration, otherwise None.
        """
        return get_in(['tool', 'poetry', 'name'], self._data, default=None)



class ProvidesAst(Protocol):
    """Protocol for providing an abstract syntax tree (AST).

    This class specifies a protocol for retrieving an abstract syntax tree
    (AST) through the `get_ast` method. Implementers of this protocol
    should provide their own logic for returning the AST, represented
    as an instance of the `Module` class.

    Attributes:
        No attributes are explicitly defined in this protocol.
    """
    def get_ast(self) -> Module:
        """
        Represents a method to retrieve the Abstract Syntax Tree (AST) in the form of a
        Module, which serves as the root node of the tree representation of the source
        code.

        Returns:
            Module: The root node of the Abstract Syntax Tree (AST).
        """
        ...



class PythonSourceFile(ProjectFile, ProvidesAst):
    """
    Represents a Python source file in a project directory.

    This class is intended to model a Python source file as part of a project.
    It extends the `ProjectFile` class and provides additional functionality
    specific to Python files, such as obtaining import statements, determining
    the Python version, and generating canonical identifiers.

    Attributes:
        _project_name (str | None): The name of the project this file belongs to,
        or None if not assigned.
    """
    def __init__(self, file_path: Path, base_path: Path, project_name: str | None = None):
        """
        Initializes an instance with attributes for managing file paths and project name.

        Args:
            file_path: The path to the specific file associated with this instance.
            base_path: The base directory path associated with this instance.
            project_name: The name of the project, optional, defaults to None.
        """
        super().__init__(file_path, base_path)
        self._project_name: str | None = project_name


    @property
    def project(self) -> str:
        """
        Gets the project name as a string.

        This property retrieves the project name stored in the `_project_name`
        attribute. It ensures that the attribute is accessed in a controlled and
        readable manner.

        Returns:
            str: The name of the project.
        """
        return self._project_name

    @property
    def module_name(self) -> str:
        return '.'.join(self._file_path.parts)

    @property
    def python_version(self) -> tuple[int, int, int]:
        """
        Returns the version of Python as a tuple consisting of major, minor, and patch
        version numbers.

        This property is used to retrieve the version of Python in use. The version is
        returned as a tuple with three integers, representing the major, minor, and
        patch components of the Python version.

        Returns:
            tuple[int, int, int]: A tuple containing the major, minor, and patch version
            numbers of the Python interpreter.
        """
        return 3, 12, 0

    @property
    def id(self) -> str:
        return f'{self._absolute_path.as_uri()}'

    @property
    def canonical_id(self):
        """
        Returns the canonical identifier for a file.

        The canonical ID is derived from the file path by removing the '.py' extension
        from the file name and joining its parts using dots. This is typically used
        to represent the file in a normalized, human-readable format.

        Returns:
            str: The canonical identifier representing the file.

        """
        return '.'.join(self._file_path.with_name(self._file_path.name.removesuffix('.py')).parts)

    def get_imports(self) -> dict[str, str]:
        """
        Retrieves a dictionary of imports from an abstract syntax tree (AST).

        This method traverses the abstract syntax tree (AST) obtained from the
        `get_ast` method of the current instance to identify all import
        statements such as `import` and `from ... import ...`. It constructs and
        returns a dictionary where keys are the imported names (or their
        aliases if specified) and values are their corresponding fully
        qualified module paths.

        Returns:
            dict[str, str]: A dictionary mapping imported names or aliases
            to their fully qualified module paths.
        """
        imports: dict[str, str] = dict()
        for node in walk(self.get_ast()):
            match node:
                case ImportFrom(module=module, names=names):
                    for name in names:
                        imports[name.asname if name.asname else name.name] = f'{module}.{name.name}'
                case Import(names=names):
                    for name in names:
                        imports[name.asname if name.asname else name.name] = name.name
        return imports

    def get_ast(self) -> Module:
        """
        Parses and returns the abstract syntax tree (AST) of the file located at the path
        specified by `_file_path`. The method reads the contents of the file as binary
        and generates an AST representation using the `parse` function.

        Returns:
            ast.AST: The abstract syntax tree representation of the file.
        """
        with self._absolute_path.open('rb') as src:
            return parse(src.read())



class PythonProjectGraph(ProjectGraph):
    """
    Represents a graph for managing Python projects.

    This class extends the base `ProjectGraph` to provide functionality
    specific to Python projects. It facilitates the addition and organization
    of Python source files within a project's graph structure.

    Attributes:
        project_name (str): Name of the current project.
    """
    def __init__(self, project_name: str = 'Project'):
        """
        Represents a class with an initializer for setting the project name.

        This class provides an initialization method that allows setting a
        default or custom project name during object creation.

        Attributes:
            project_name (str): The name of the project being initialized.
        """
        super().__init__(project_name)


    def add_python_file(self, python_file: PythonSourceFile, attributes: dict[str, JSONType] | None = None):
        """
        Adds a Python source file to the system with optional attributes.

        This method integrates a Python source file into the configuration or
        tracking system, associating it with its type and any additional attributes
        that provide metadata or specific processing details.

        Args:
            python_file (PythonSourceFile): The Python source file to be added.
            attributes (dict[str, JSONType] | None): Optional metadata or additional
                attributes associated with the Python file.
        """
        self.add_file(python_file, 'Python File', attributes)



class PythonProjectLocation(ProjectLocation):
    """
    Represents a Python project location on the filesystem.

    This class extends the functionality of a generic project location to handle
    Python-specific project settings and files. It manages paths, identifies Python
    project files, and retrieves Python project details like its name.

    Attributes:
        _pyproject_file (PyProjectFile): A reference to the pyproject.toml file
            associated with the Python project.
    """
    def __init__(self, path: Path):
        super().__init__(path)
        self._pyproject_file: PyProjectFile = PyProjectFile(path.joinpath('pyproject.toml'))

    @property
    def project_name(self) -> str:
        """
        Retrieves the name of the project from the pyproject file.

        This property accessor fetches the name of the project using the
        associated `pyproject_file` attribute, which represents the
        pyproject configuration file.

        Attributes:
            _pyproject_file (Path): The path object representing the pyproject file.

        Returns:
            str: The name of the project as specified in the pyproject file.
        """
        return self._pyproject_file.name

    def _is_project_file(self, file_path: Path) -> bool:
        """
        Determines if the given file path corresponds to a project file.

        This method evaluates whether the file located at the provided path has
        a `.py` extension, indicating that it is a Python file typically associated
        with projects.

        Args:
            file_path: File system path to the file being checked.

        Returns:
            bool: True if the file has a `.py` extension, otherwise False.
        """
        return file_path.suffix == '.py'

    def files(self) -> Iterable[PythonSourceFile]:
        for file in super().files():
            yield PythonSourceFile(file.path, file.base_dir.absolute(), self._pyproject_file.name)

