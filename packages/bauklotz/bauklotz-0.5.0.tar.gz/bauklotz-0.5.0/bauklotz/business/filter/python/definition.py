"""

@Component[Layer] Filter
@Component[SubLayer] Python
"""

from ast import walk, ClassDef, parse, If, IfExp, ExceptHandler, Match, For, While, Name, Subscript, Attribute, BinOp, BitOr
from collections.abc import Sequence
from functools import singledispatchmethod
from typing import Self, Iterable, Protocol

from toolz import count, drop, compose

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.python.definition import PythonClass, ClassMethod, DefinitionInspector, InspectionError
from bauklotz.reporting.item.python.project import PythonSourceFile


class PythonClassConfig(FilterConfig):
    def __init__(self, ignore_dataclasses: bool = False, inspect: bool = True):
        self._ignore_dataclasses: bool = ignore_dataclasses
        self._inspect: bool = inspect

    @property
    def inspect(self) -> bool:
        return self._inspect


    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(bool(data.get('ignore_dataclasses', False)), bool(data.get('inspect', True)))


class PythonClassFilter(Filter[PythonSourceFile, PythonClass, PythonClassConfig]):
    def __init__(self, name: str, config: PythonClassConfig):
        super().__init__(name, config)

    def process(self, item: PythonSourceFile) -> Iterable[PythonClass]:
        for element in walk(item.get_ast()):
            if isinstance(element, ClassDef):
                yield self._build_result_item(item, element)
                item.facts.extend('classes', element.name)

    def _build_result_item(self, item: PythonSourceFile, element: ClassDef) -> PythonClass:
        lines: Sequence[str] = item.content.splitlines()
        class_item: PythonClass = PythonClass(
            item.canonical_id,
            element.name,
            '\n'.join(lines[element.lineno -1 : element.end_lineno]),
            item
        )
        self._handle_generics(class_item, element)
        if self.config.inspect:
            self._inspect(class_item)
        return class_item

    def _inspect(self, class_item: PythonClass) -> None:
        inspector: DefinitionInspector = DefinitionInspector()
        try:
            class_obj: object = inspector.inspect(class_item.module, class_item.name)
            if isinstance(class_obj, type):
                class_item.facts.set('abstract', bool(getattr(class_obj, '__abstractmethods__', False)))
                class_item.facts.set('interface', bool(getattr(class_obj, '_is_protocol', False)))
        except InspectionError as error:
            pass


    def _handle_generics(self, item: PythonSourceFile, element: ClassDef) -> None:
        generics: dict[str, str] = dict()
        for generic in element.type_params:
            generics[generic.name] = self._parse_generic_bound(generic.bound)
        item.facts.set('type_parameters', generics)

    @singledispatchmethod
    def _parse_generic_bound(self, bound) -> JSONType:
        return str(bound)

    @_parse_generic_bound.register
    def _parse_name(self, bound: Name) -> JSONType:
        return bound.id

    @_parse_generic_bound.register
    def _parse_op(self, bound: BinOp) -> JSONType:
        op: str = bound.op.__class__.__name__
        match bound.op:
            case BitOr(): op = 'or'
        return dict(op=op, left=self._parse_generic_bound(bound.left), right=self._parse_generic_bound(bound.right))

class PythonSuperclassConfig(FilterConfig):
    def __init__(self):
        pass

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls()

class PythonSuperclassFilter(Filter[PythonClass, PythonClass, PythonSuperclassConfig]):
    def __init__(self, name: str, config: PythonSuperclassConfig = PythonSuperclassConfig()):
        super().__init__(name, config)
        self._imports: dict[str, str] = {}
        self._module: str = ''

    def process(self, item: PythonClass) -> Iterable[PythonClass]:
        self._imports = item.source.get_imports()
        self._module = item.source.canonical_id
        match next(drop(1, walk(parse(item.body)))):
            case ClassDef(bases=bases):
                item.facts.set(
                    'superclass',
                    list(map(compose(self._get_canonical_base_name, self._parse_superclass), bases))
                )
                yield item
            case _: raise TypeError("Invalid class definition")

    def _get_canonical_base_name(self, name: str) -> str:
        if name in self._imports:
            return self._imports[name]
        if '.' in name:
            base_mod, *path = name.split('.')
            if base_mod in self._imports:
                return f'{self._imports[base_mod]}.{".".join(path)}'
        return f'{self._module}.{name}'


    @singledispatchmethod
    def _parse_superclass(self, base) -> str:
        return str(base)

    @_parse_superclass.register
    def _parse_name(self, base: Name) -> str:
        return base.id

    @_parse_superclass.register
    def _parse_subscript(self, base: Subscript) -> str:
        return self._parse_superclass(base.value)

    @_parse_superclass.register
    def _parse_attribute(self, base: Attribute) -> str:
        return f'{self._parse_superclass(base.value)}.{self._parse_superclass(base.attr)}'


class PythonMethodConfig(FilterConfig):
    def __init__(self, ignore_special_methods: bool = False, ignore_private: bool = False):
        self._ignore_special_methods: bool = ignore_special_methods
        self._ignore_private: bool = ignore_private


    @property
    def ignore_special(self) -> bool:
        """
        Gets the value indicating whether special methods are ignored.

        This property retrieves the boolean value that determines if special
        methods (e.g., methods with double underscores like `__init__` or
        `__str__`) are being ignored in certain operations or functionality
        within the scope of this property.

        Returns:
            bool: True if special methods are ignored, False otherwise.
        """
        return self._ignore_special_methods

    @property
    def ignore_private(self) -> bool:
        """
            Retrieves the value of the `_ignore_private` attribute.

            This property indicates whether private attributes or elements should be ignored.
            It is used to manage filtering logic or behavior concerning private members.

            Returns:
                bool: The current value of the `_ignore_private` attribute.
        """
        return self._ignore_private

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(bool(data.get('ignore_special_methods', False)), bool(data.get('ignore_private', False)))


class PythonMethodFilter(Filter[PythonClass, ClassMethod, PythonMethodConfig]):
    def __init__(self, name: str, config: PythonMethodConfig):
        super().__init__(name, config)


    def process(self, item: PythonClass) -> Iterable[ClassMethod]:
        for method in filter(self._keep_method, item.analyze_body()):
            item.facts.extend('methods', method.name)
            yield method


    def _keep_method(self, method: ClassMethod) -> bool:
        return not any(
            (
                method.name.startswith('__') and self.config.ignore_special,
                method.name.startswith('_') and self.config.ignore_private
            )
        )


class PythonStatementLengthConfig(FilterConfig):
    def __init__(self, max_length: int = 10):
        self._max_length: int = max_length

    @property
    def max_length(self) -> int:
        return self._max_length

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data.get('max_length', 10))


class PythonStatementLengthFilter(Filter[PythonClass | ClassMethod, PythonClass | ClassMethod, PythonStatementLengthConfig]):
    def __init__(self, name: str, config: PythonStatementLengthConfig):
        super().__init__(name, config)

    def process(self, item: PythonClass | ClassMethod) -> Iterable[PythonClass | ClassMethod]:
        length: int = count(filter(None, map(str.strip, item.body.splitlines())))
        item.facts.set('statement_length', length)
        item.facts.set('statement_to_long', length > self.config.max_length)
        yield item


class PythonCyclicComplexityConfig(FilterConfig):
    def __init__(self, method: str = 'simple'):
        self._method: str = method

    @property
    def method(self) -> str:
        return self._method

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(data.get('method', 'simple'))


class PythonCyclicComplexityFilter(Filter[ClassMethod, ClassMethod, PythonCyclicComplexityConfig]):
    def __init__(self, name: str, config: PythonCyclicComplexityConfig):
        super().__init__(name, config)

    def process(self, item: ClassMethod) -> Iterable[ClassMethod]:
        complexity: int = 1
        match self.config.method:
            case 'simple': complexity = self._simple_complexity(item)
            case _: raise ValueError(f"Invalid method: {self.config.method}")
        item.facts.set('cyclic_complexity', complexity)
        yield item


    def _simple_complexity(self, item: ClassMethod) -> int:
        complexity: int = 1
        for node in walk(parse(item.body)):
            match node:
                case If() | IfExp() | ExceptHandler() | For() | While(): complexity += 1
                case Match(cases=cases): complexity += len(cases)
        return complexity