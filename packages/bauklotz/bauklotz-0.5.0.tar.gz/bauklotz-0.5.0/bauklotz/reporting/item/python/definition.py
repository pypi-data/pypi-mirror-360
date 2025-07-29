from _ast import Module
from ast import parse, ClassDef, FunctionDef, walk, Name, arguments, arg, BinOp, Subscript, Tuple, TypeVar
from collections.abc import Iterable, Sequence
from functools import singledispatchmethod
from importlib import import_module
from importlib.util import find_spec
from itertools import takewhile
from pathlib import Path
from sys import version_info

from stdlib_list import stdlib_list
from toolz import take, drop

from bauklotz.reporting.item import Item
from bauklotz.reporting.item.python.project import PythonSourceFile, ProvidesAst
from bauklotz.reporting.types import JSONType


class IndentNormalizer:
    """
    A utility class for normalizing indentation of string bodies.

    This class provides functionality to normalize the indentation of a
    multi-line string, optionally replacing tabs with a specified number
    of spaces.

    Attributes:
        _tabs_to_n_spaces (int | None): Number of spaces to replace tabs with.
            If None, tabs are not replaced.
    """
    def __init__(self, tab_to_n_spaces: int | None = None):
        self._tabs_to_n_spaces: int | None = tab_to_n_spaces

    def __call__(self, body: str):
        """
        Processes the given string by normalizing its indentation and optionally replacing tabs with spaces.

        The function determines the common leading whitespace used for indentation, removes it from every
        line in the given string, and replaces tabs with a specified number of spaces if the option is enabled.

        Args:
            body (str): The input string whose indentation and tabs are to be processed.

        Returns:
            str: A string with normalized indentation and optionally replaced tabs.
        """
        prefix: str = ''.join(takewhile(str.isspace, body))
        stripped: str = '\n'.join(line.removeprefix(prefix) for line in body.splitlines())
        if self._tabs_to_n_spaces:
            return stripped.replace('\t', ' '*self._tabs_to_n_spaces)
        else:
            return stripped

class TypeAnalyzer:
    """
    Analyzes various Python AST types to extract meaningful representations.

    The `TypeAnalyzer` class provides methods to analyze and transform AST (Abstract Syntax Tree) nodes
    into simplified or structured representations. This is useful for applications such as static
    analysis, code generation, or understanding Python type annotations.

    Attributes:
        analyze (Callable): A single-dispatch method registered to handle different AST node types
            with custom implementations for specific types.
    """
    def __init__(self):
        pass

    @singledispatchmethod
    def analyze(self, item):
        """
        Method to analyze the given item by converting it to its string representation.

        The method uses `functools.singledispatchmethod` to allow different behaviors for
        different input types, enabling the definition of type-specific variations by
        registering corresponding implementations.

        Args:
            item: The item to be analyzed.
        """
        return str(item)

    @analyze.register
    def _analyze_name(self, item: Name):
        return item.id

    @analyze.register
    def _analyze_or(self, item: BinOp):
        return dict(_type='union', left=self.analyze(item.left), right=self.analyze(item.right))

    @analyze.register
    def _analyze_arg(self, item: arg):
        return dict(_type='argument', name=item.arg, type=self.analyze(item.annotation))

    @analyze.register
    def _analyze_type_var(self, item: TypeVar):
        return dict(_type='type_var', name=item.name, bound=self.analyze(item.bound))

    @analyze.register
    def _analyze_tuple(self, item: Tuple):
        return [self.analyze(elt) for elt in item.elts]

    @analyze.register
    def _analyze_subscript(self, item: Subscript):
        return dict(_type='generic', name=self.analyze(item.value), type_parameter=self.analyze(item.slice))





class ClassMethod(Item, ProvidesAst):
    """
    Representation of a class method.

    This class encapsulates the necessary information about a method that belongs
    to a specific class, including its name, body, arguments, return type,
    and the class it belongs to. It provides functionality to analyze and
    serialize this information, allowing for detailed inspection of the method's
    structure and metadata.

    Attributes:
        _belongs_to_class (str): Fully qualified name of the class to which this
            method belongs.
        _name (str): Name of the method.
        _body (str): Source code of the method body, normalized for indentation.
        _ast (FunctionDef | None): Parsed abstract syntax tree (AST) representation
            of the method, if applicable.

    Properties:
        id (str): Fully qualified identifier of the method, combining the class
            and method name.
        body (str): Source code of the method, as a string.
        name (str): Name of the method.
        args (JSONType): Analyzed arguments of the method, including their types.
        generic_parameter (JSONType): Analyzed generic type parameters of the
            method, if any.
        return_value (str | None): Return type of the method, if defined.
        belongs_to (str): Fully qualified name of the class this method belongs to.
    """
    def __init__(self, class_path: str, name: str, body: str):
        """
        Represents an initializer method for a specific class that sets up necessary
        attributes, processes a provided body string through an IndentNormalizer instance,
        and assigns the processed value to an internal attribute.

        The initializer is designed for subclasses that extend functionality requiring
        AST (Abstract Syntax Tree) handling for function definitions, although the AST
        attribute is initialized as None.

        Args:
            class_path: The string representation of the class to which the function
                belongs.
            name: The name of the function as a string.
            body: A string containing the body of the function to be processed and
                normalized.
        """
        self._belongs_to_class: str = class_path
        self._name: str = name
        self._body: str = IndentNormalizer()(body)
        self._ast: FunctionDef | None = None
        super().__init__()

    @property
    def id(self) -> str:
        """
        Returns a unique identifier for the instance combining class ownership and name.

        Attributes:
            id (str): A unique identifier consisting of the class it belongs to and
                its name, separated by a colon.
        """
        return f'{self._belongs_to_class}:{self._name}'

    @property
    def body(self) -> str:
        """
        Retrieves the body content of the instance.

        This property provides access to the `_body` attribute of the instance,
        representing the textual content. It is a getter method that allows reading
        the `_body` value as a string.

        Returns:
            str: The body content of the instance.
        """
        return self._body

    @property
    def name(self) -> str:
        """
        Represents a property that retrieves the private `_name` attribute.

        This property provides read-only access to the value of the private `_name`
        attribute.

        Attributes:
            _name (str): Internal storage for the name attribute.

        Returns:
            str: The value of the `_name` attribute.
        """
        return self._name

    @property
    def args(self) -> JSONType:
        """
        Returns the arguments of the function definition in a specific analyzed format.

        This property dynamically loads the abstract syntax tree (AST) representation
        of a function and extracts its arguments. The arguments are then analyzed
        using a type analyzer tool that processes their type information. The final
        result is a list of analyzed arguments.

        Attributes:
            args (JSONType): Provides the analyzed list of arguments for the function
                definition extracted from the AST.

        Returns:
            list: A list of analyzed arguments derived from the function's AST.
        """
        self._load_ast()
        match self._ast:
            case FunctionDef(args=arguments(args=args)):
                analyzer: TypeAnalyzer = TypeAnalyzer()
                return list(map(analyzer.analyze, args))

    def get_ast(self) -> Module:
        return parse(self.body)

    @property
    def generic_parameter(self) -> JSONType:
        """
        Retrieves and analyzes the generic parameters from the abstract syntax tree (AST) of a function
        definition. The method processes type parameters, if present, and returns their analyzed forms.

        Returns:
            JSONType: A list of analyzed type parameters based on the AST of the function definition.
        """
        self._load_ast()
        match self._ast:
            case FunctionDef(type_params=params):
                return list(map(TypeAnalyzer().analyze, params))

    @property
    def return_value(self) -> str | None:
        """
        Gets the return type of a function if explicitly defined, else returns None.

        The method analyzes the abstract syntax tree (AST) of a function definition
        to determine whether a return type annotation is present. If an annotation
        exists, it retrieves and returns the type as a string; otherwise, it
        returns None.

        Returns:
            str | None: The return type of the function as a string, or None if not
            explicitly defined.
        """
        self._load_ast()
        match self._ast:
            case FunctionDef(returns=Name(id=return_type)):
                return str(return_type)
            case _: return None

    @property
    def belongs_to(self) -> str:
        """
        Returns the class or entity to which the object belongs.

        This property retrieves the association of the current instance with a
        specific class or entity. It is primarily used to identify ownership
        or relationship within the application's context.

        Returns:
            str: The name of the class or entity to which the object belongs.
        """
        return self._belongs_to_class

    def _load_ast(self) -> None:
        if self._ast:
            return
        else:
            self._ast = next(drop(1, walk(parse(self.body))))


    def serialize(self) -> JSONType:
        """
        Serializes the current object state into a JSON-compatible format.

        This method converts the instance attributes of the object into a JSON-
        compatible dictionary. The attributes included in the serialization are
        class, name, body, args, returns, and generics. The purpose of this
        method is to allow easy exporting of the internal state or for
        interfacing with systems requiring JSON structures.

        Returns:
            dict: A dictionary containing the serialized representation of the
            object state. The keys in the dictionary correspond to the instance
            attributes and their respective values.
        """
        return {
            'class': self._belongs_to_class,
            'name': self._name,
            'body': self._body,
            'args': self.args,
            'returns': self.return_value,
            'generics': self.generic_parameter
        }

    def __len__(self) -> int:
        """
        Calculates and returns the number of lines in the stored text body. A line
        is determined by the occurrence of the newline character ('\n'). If no
        newline characters are present, the method will count a single line.

        Returns:
            int: The number of lines in the `self._body` attribute.
        """
        return self._body.count('\n') + 1



class DefinitionTracer:
    """Tracks and traces the definition of a given identifier within a module.

    This class is designed to locate the definition of a particular item within
    a specified module. It determines whether the definition is within the given
    module or originates from an external source and returns the fully-qualified
    name of the definition. This can be particularly useful for analyzing
    dependencies or understanding the source of third-party imports.

    Attributes:
        None
    """
    def __init__(self, internal_modules: set[str] | str | None = None, python_version: str | None = None):
        self._major, self._minor, *_ = python_version.split('.') if python_version else version_info
        internal_modules = {internal_modules} if isinstance(internal_modules, str) else internal_modules
        self._internal_modules: set[str] = internal_modules or set()
        self._stdlib: set[str] = set(stdlib_list('.'.join(take(2, map(str, version_info)))))

    def origin_type(self, module: str) -> str:
        """
        Determines the origin type of a given module.

        This method classifies a module as belonging to the standard library,
        internal modules, or third-party modules based on predefined attributes.

        Args:
            module (str): The full name of the module.

        Returns:
            str: The origin type of the module, which can be one of the following:
                 'stdlib', 'internal', or 'third-party'.
        """
        base_module: str = module.split('.', 1)[0]
        if base_module in self._stdlib:
            return 'stdlib'
        else:
            return 'internal' if base_module in self._internal_modules else 'third-party'





    def trace(self, module: str, name: str) -> str:
        """
        Trace the origin of a module and retrieve its path or construct a fully qualified
        name string. This function attempts to locate the source code path of the given
        module, and if it exists, processes it to find the origin. Otherwise, it returns
        a string in the format of 'module.name'.

        Args:
            module (str): The name of the module for which the source path or origin
                string needs to be determined.
            name (str): A name associated with the module, typically referring to a
                member or attribute for which the origin must be traced.

        Returns:
            str: If the module's source path exists, it returns the origin based on the
                path, module, and name provided. Otherwise, it returns a string in the
                format of 'module.name'.
        """
        path: Path | None = self._get_module_source_path(module)
        if path and path.exists():
            return self._origin(path, module, name)
        else:
            return f'{module}.{name}'

    @staticmethod
    def _get_module_source_path(module_path: str) -> Path | None:
        spec = find_spec(module_path)
        if spec and spec.origin:
            return Path(spec.origin)
        return None

    def _origin(self, path: Path, module: str, item: str) -> str:
        source: PythonSourceFile = PythonSourceFile(path, path.parent)
        if third_party_import := source.get_imports().get(item):
            module, name = third_party_import.rsplit('.', 1)
            return self.trace(module, name)
        else:
            return f'{module}.{item}'


class InspectionError(ImportError):
    """Custom exception for errors occurring during inspection.

    This exception is raised to signal specific issues related to the
    inspection process in the application. It extends the standard
    ImportError to provide more context and domain-specific handling for
    such scenarios.

    Attributes:
        message (str): The error message providing details about the
            inspection error.
    """
    def __init__(self, message: str):
        super().__init__(message)


class DefinitionInspector:
    """
    Provides functionality to inspect modules and dynamically retrieve attributes or
    callables from them.

    The DefinitionInspector class is designed to dynamically analyze modules and
    return specified attributes or callables. This can be particularly useful for
    dynamic loading of components in extensible or configurable systems.

    Attributes:
        None
    """
    def __init__(self):
        pass

    def inspect(self, module: str, name: str):
        """
        Inspects a given module to retrieve a specified attribute or callable.

        This method takes the name of a module, dynamically imports it, and attempts to
        retrieve the specified attribute or callable within the module. If the module
        cannot be imported or the attribute does not exist, an ImportError is raised
        with an appropriate error message.

        Args:
            module (str): The name of the module to be imported.
            name (str): The name of the attribute or callable to retrieve from the
                specified module.

        Raises:
            ImportError: Raised if the module cannot be imported or if the specified
                attribute does not exist within the module.

        Returns:
            Any: The attribute or callable retrieved from the specified module.
        """
        try:
            module = import_module(module)
            return getattr(module, name)
        except (ImportError, AttributeError) as error:
            raise InspectionError(f"Could not load {name} from {module}: {error}")


class PythonClass(Item, ProvidesAst):
    """
    Represents a Python class and provides functionality for analyzing and serializing its components.

    This class models a Python class within a source file. It allows extraction of details such as
    methods defined within the class and provides utility methods to serialize class information
    and analyze the class body. It also provides tracing functionality to determine the origin of
    the class definition in a project context.

    Attributes:
        _module (str): Module name where the class is defined, with '__init__' removed if present.
        _name (str): Name of the class.
        _body (str): Raw source code of the class body.
        _source (PythonSourceFile): Python source file object containing the class definition.
        _methods (list[ClassMethod]): List of analyzed method objects belonging to the class.
    """
    def __init__(self, module: str, name: str, body: str, source: PythonSourceFile):
        """
        Initializes a class instance with module, name, body, and source attributes,
        and prepares an empty list for methods. This is a constructor method responsible
        for setting up the basic structure of the class, including assigning values to
        necessary attributes and inheriting from a parent class.

        Args:
            module (str): The module name where this class is located. If the module
                name ends with '.__init__', it is replaced with an empty string.
            name (str): The name of the class being initialized.
            body (str): The body content of the class as a string.
            source (PythonSourceFile): The source file object that contains information
                about the Python source file where the class is defined.
        """
        self._module: str = module.replace('.__init__', '')
        self._name: str = name
        self._body: str = body
        self._source: PythonSourceFile = source
        self._methods: list[ClassMethod] = list()
        super().__init__()

    def get_ast(self) -> Module:
        return parse(self.body)

    @property
    def id(self) -> str:
        return f'{self._module}.{self._name}'

    @property
    def methods(self) -> Sequence[ClassMethod]:
        """
        Retrieve and return a tuple containing all methods associated with the instance.

        This property provides access to the sequence of methods that are stored in
        the internal `_methods` attribute of the class. It ensures that the data
        is returned in an immutable form (as a tuple), preventing modifications
        to the collection of methods externally.

        Returns:
            Sequence[ClassMethod]: A tuple representing the collection of class methods
            associated with the instance.
        """
        return tuple(self._methods)

    @property
    def module(self) -> str:
        """
        Gets the module name associated with the current object.

        Returns:
            str: The name of the module associated with this object.
        """
        return self._module

    @property
    def body(self) -> str:
        """
        Gets the body of the object.

        This property is a getter for the `_body` attribute, which holds the main
        content or body of the object in the form of a string.

        Returns:
            str: The content or body stored in the `_body` attribute.
        """
        return self._body

    @property
    def name(self) -> str:
        """
        Returns the name associated with the object.

        The `name` property retrieves the private attribute `_name`, which represents the
        name of the instance or the value assigned for identification purposes.

        Returns:
            str: The name of the instance.
        """
        return self._name

    @property
    def source(self) -> PythonSourceFile:
        """
        Retrieves the Python source file associated with the current object.

        This property provides access to the `PythonSourceFile` instance that
        represents the source file for the object. It allows consumers of the class
        to access metadata or content from the file without directly modifying it.

        Returns:
            PythonSourceFile: The associated Python source file instance.
        """
        return self._source

    def serialize(self) -> JSONType:
        """
        Represents the functionality to serialize an object into a JSON-compatible
        dictionary format. Intended for internal use to standardize object structure
        serialization including module name, object name, and its body content.

        Returns:
            JSONType: A dictionary containing the serialized object representation
            with the following keys:
                - module: The name of the module.
                - name: The name of the object.
                - body: The main content or body of the object.
        """
        return dict(module=self._module, name=self._name, body=self._body)

    def analyze_body(self) -> Iterable[ClassMethod]:
        """
        Analyzes the body of a class to identify and yield methods based on specific criteria.

        This method looks through the body of a specified class definition, analyzes each
        element in the body, and reports any identified methods. The results are stored in
        an internal list of methods and yielded sequentially.

        Returns:
            Iterable[ClassMethod]: An iterable of analyzed class methods.

        """
        definition: ClassDef = self._find_class(self.body)
        for element in definition.body:
            if (analysis := self._report_element(element)) is not None:
                self._methods.append(analysis)
                yield analysis

    def trace_origin(self) -> tuple[str, str]:
        """
        Traces the origin of a definition within a project's source code and retrieves its origin model
        and type.

        Returns:
            tuple[str, str]: A tuple containing the origin model and its corresponding origin type.
        """
        tracer: DefinitionTracer = DefinitionTracer(self._source.project)
        origin_model: str = tracer.trace(self._module, self.name)
        return origin_model, tracer.origin_type(origin_model)


    @staticmethod
    def _find_class(body: str) -> ClassDef:
        for element in walk(parse(body)):
            if isinstance(element, ClassDef):
                return element
        raise LookupError(f"No class found in body {body}")

    @singledispatchmethod
    def _report_element(self, element) -> ClassMethod | None:
        print(element)
        return None

    @_report_element.register
    def _report_method(self, element: FunctionDef) -> ClassMethod:
        lines: Sequence[str] = self._body.splitlines()
        return ClassMethod(
            self.id,
            element.name,
            '\n'.join(lines[element.lineno - 1: element.end_lineno])
        )


