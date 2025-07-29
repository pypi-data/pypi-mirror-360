from ast import expr, walk, get_docstring, Import, ImportFrom, stmt
from collections import defaultdict
from typing import Iterable, Self

from bauklotz.business.filter import Filter, FilterConfig
from bauklotz.reporting.item.python.definition import PythonClass, ClassMethod
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.python.dependency import PythonImport
from bauklotz.reporting.item.python.project import PythonSourceFile

_STATEMENT_COUNT_LABEL: str = 'statement_count'
DOCSTRING_LABEL: str = 'documentation'

class PythonStatementCountConfig(FilterConfig):
    def __init__(self, include_ratio: bool = True):
        self._include_ratio: bool = include_ratio

    @property
    def include_ratio(self) -> bool:
        return self._include_ratio


    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data.get("include_ratio", True))


class PythonStatementCountFilter(Filter[PythonSourceFile | PythonClass | ClassMethod, PythonSourceFile, PythonStatementCountConfig]):
    """
    Represents a filter for counting and analyzing Python statements within a source file,
    class, or method.

    This class is designed to process Python source files, classes, or methods to count the
    number of Python statements and lines of code. It also calculates additional metrics
    such as the ratio of expressions to lines of code if configured. The results of the
    analysis are stored as facts for subsequent use.

    Attributes:
        provides_facts (frozenset[str]): Identifies the facts that this filter provides. In
            this case, `_STATEMENT_COUNT_LABEL`, which represents the count of Python
            statements is one of the provided facts.
    """
    provides_facts: frozenset[str] = frozenset({_STATEMENT_COUNT_LABEL})

    def __init__(self, name: str, config: PythonStatementCountConfig):
        super().__init__(name, config)

    def process[I: PythonSourceFile | PythonClass | ClassMethod](self, item: I) -> Iterable[I]:
        n_statements: int = 0
        code_lines: set[int] = set()
        for node in (node for node in walk(item.get_ast())):
            if isinstance(node, expr):
                n_statements += 1
            if isinstance(node, stmt):
                code_lines.add(node.lineno)

        item.facts.set(_STATEMENT_COUNT_LABEL, n_statements)
        item.facts.set('lines_of_code', len(code_lines))
        if self.config.include_ratio:
            ratio: float = n_statements / len(code_lines) if len(code_lines) > 0 else 0.0
            item.facts.set('expression_loc_ratio', round(ratio, 2))
        yield item


class PythonModuleDocstringConfig(FilterConfig):
    """
    Configuration class for handling Python module documentation settings.

    This class is used to manage the configuration options for documentation,
    including the default value for certain settings. It provides methods to
    initialize, access, and deserialize the configuration from given input data.

    Attributes:
        _default (str | None): Internal storage for the default configuration
            value. Can be None if no default is set.
    """
    def __init__(self, default: str | None = None):
        self._default: str | None = default

    @property
    def default(self):
        """
        Gets the default value for the property.

        This property retrieves the current value stored in the `_default` attribute.
        It ensures an encapsulated access to the `_default` attribute, providing a
        getter functionality without exposing direct modification to external entities.

        Returns:
            Any: The current value stored in the `_default` attribute.
        """
        return self._default

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data.get('default', None))


class PythonModuleDocstringFilter(Filter[PythonSourceFile, PythonSourceFile, PythonModuleDocstringConfig]):
    """
    Provides functionality to filter Python source files for module docstrings.

    This class represents a filter that processes Python source files to extract
    or apply module-level docstrings. It leverages the configuration to determine
    default docstrings where none are present, and associates extracted or resolved
    docstrings with the appropriate fact storage. Its purpose is to ensure all
    processed Python modules meet certain docstring requirements, assisting in
    documentation compliance or enforcement use cases.

    Attributes:
        provides_facts (frozenset[str]): A set of fact labels this filter
            provides, specifically indicating the module-level docstring fact
            label.
    """
    provides_facts: frozenset[str] = frozenset({DOCSTRING_LABEL})
    def __init__(self, name: str, config: PythonStatementCountConfig):
        super().__init__(name, config)


    def process(self, item: PythonSourceFile) -> Iterable[PythonSourceFile]:
        """
        Processes a Python source file to extract its docstring and store it in the item fact store.

        This function retrieves the docstring from the provided Python source file's AST
        (Abstract Syntax Tree). If a docstring isn't present, it uses a default docstring
        from the configuration. The extracted or default docstring is then stored in the
        item fact store under a designated label. Finally, it yields the processed Python
        source file.

        Args:
            item: Python source file to be processed.

        Yields:
            PythonSourceFile: The processed source file with its docstring extracted and stored.
        """
        docstring: str = get_docstring(item.get_ast()) or self.config.default
        item.facts.set(DOCSTRING_LABEL, docstring)
        yield item


class PythonImportConfig(FilterConfig):
    """
    Represents a configuration for handling Python imports as part of a filtering process.

    This class is a specialized form of FilterConfig used specifically in managing
    Python import configurations. It includes methods for deserialization to instantiate
    the class based on serialized data. Useful in scenarios where configurations associated
    with Python import handling need to be modularized and dynamically created.

    Attributes:
        None
    """
    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls()


class PythonImportFilter(Filter[PythonSourceFile, PythonImport, PythonImportConfig]):
    """Represents a filter for analyzing and processing Python imports.

    This class is used to collect and process `import` and `from ... import ...`
    statements from the abstract syntax tree (AST) of a Python source file. It
    extracts the modules and their imported members, along with any alias information,
    providing a structured representation of the imports.

    Attributes:
        name (str): The name of the filter.
        config (PythonImportConfig): Configuration specific to the Python import filter.
    """
    def __init__(self, name: str, config: PythonImportConfig):
        super().__init__(name, config)

    def process(self, item: PythonSourceFile) -> Iterable[PythonImport]:
        """
        Processes the abstract syntax tree (AST) of a given Python source file to extract
        import statements, including both `import` and `from ... import ...`, and yields
        parsed information as PythonImport objects.

        This function examines each statement in the parsed AST of a Python source file to
        identify its import declarations. It supports both standard imports and imports
        with aliases. For each import, it collects the module name, imported names, and
        optional aliases, assembling them into a structured dictionary. The function
        subsequently yields a PythonImport object for each discovered module, along with
        its associated imports.

        Args:
            item (PythonSourceFile): The input Python source file whose AST is to be
                analyzed to extract import statements.

        Yields:
            PythonImport: An iterable of parsed import data, including the originating
                source file, the module name, and a dictionary of imported names and
                their aliases.
        """
        imports: dict[str, set[tuple[str, str | None]]]  = defaultdict(set)
        for statement in walk(item.get_ast()):
            match statement:
                case ImportFrom(module=module, names=names):
                    for name in names:
                        imports[module].add((name.name, name.asname))
                case Import(names=names):
                    for name in names:
                        imports[name.name].add(("*", None))
        for module, module_imports in imports.items():
            yield PythonImport(item, module, dict(module_imports))