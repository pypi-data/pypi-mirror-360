from abc import ABC, abstractmethod
from re import Pattern, compile as regex, Match, MULTILINE
from typing import Self, Iterable
from ast import get_docstring

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.business.filter.python.file import DOCSTRING_LABEL
from bauklotz.reporting.item.graph import Graph, GraphNode
from bauklotz.reporting.item.python.definition import PythonClass, DefinitionTracer
from bauklotz.reporting.types import JSONType
from bauklotz.reporting.item.generic.group import Module, Component
from bauklotz.reporting.item.python.project import PythonSourceFile


class PythonModuleConfig(FilterConfig):
    def __init__(self):
        pass


    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls()



class PythonModuleFilter(Filter[PythonSourceFile, Module, PythonModuleConfig]):
    def __init__(self, name: str, config: PythonModuleConfig):
        super().__init__(name, config)

    def process(self, item: PythonSourceFile) -> Iterable[Module]:
        item.facts.set('part_of_module', item.canonical_id)
        yield Module(item.canonical_id, (item, ))


class ComponentExtractor(ABC):
    @abstractmethod
    def get_components(self, item: Module[PythonSourceFile]) -> Iterable[Component]:
        """
        Abstract method to retrieve components associated with a given module. This method
        must be implemented in any subclass and its purpose is to extract or define a
        list of components related to the provided module input.

        Args:
            item (Module): The module instance for which the components need to be
                retrieved.

        Returns:
            Iterable[Component]: An iterable object containing components derived
                from the provided module.
        """

class DocstringExtractor(ComponentExtractor):
    def __init__(self, pattern: str, flags: int = MULTILINE):
        self._pattern: Pattern = regex(pattern, flags)

    def get_components(self, item: Module[PythonSourceFile]) -> Iterable[Component]:
        for file in item:
            docstring: str | None = file.facts.get(DOCSTRING_LABEL) or get_docstring(file.get_ast())
            yield from self._extract(docstring)

    def _extract(self, docstring: str | None) -> Iterable[Component]:
        if docstring:
            for match in self._pattern.finditer(docstring):
                yield self._build_component(match)
        else:
            return()

    @staticmethod
    def _build_component(match: Match) -> Component:
        if len(match.groups()) >= 2:
            return Component(match.group(1), match.group(2))

class PythonComponentConfig(FilterConfig):
    def __init__(self, method: str, **kwargs):
        match method:
            case 'docstring': self._extractor = DocstringExtractor(**kwargs)
            case _: raise NameError(f'Unknown component extractor method: {method}')

    @property
    def extractor(self) -> ComponentExtractor:
        return self._extractor

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(**data)


class PythonComponentFilter(Filter[Module, Component, PythonComponentConfig]):
    def __init__(self, name: str, config: PythonComponentConfig):
        super().__init__(name, config)
        self._components: set[Component] = set()

    def process(self, item: Module) -> Iterable[Component]:
        for component in self._config.extractor.get_components(item):
            self._components.add(component)
            component.add_module(item)
            item.facts.set('part_of_component', component.canonical_id)
        return ()

    def close(self) -> Iterable[Component]:
        yield from self._components


class PythonClassHierarchyConfig(FilterConfig):
    def __init__(self, explicit_internal_modules: set[str] | None = None):
        self._explicit_internal_modules: set[str] = explicit_internal_modules or set()

    @property
    def internal_modules(self) -> set[str]:
        return self._explicit_internal_modules

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(set(filter(None, map(str.strip, data.get('internal_modules', "").split('.')))))


class PythonClassHierarchyFilter(Filter[PythonClass, Graph, PythonClassHierarchyConfig]):
    def __init__(self, name: str, config: PythonClassHierarchyConfig):
        super().__init__(name, config)
        self._items: list[PythonClass] = list()
        self._graph: Graph = Graph()
        self._internal_modules: set[str] = set()

    def process(self, item: PythonClass) -> Iterable[Graph]:
        self._items.append(item)
        self._internal_modules.add(item.source.project)
        return ()


    def close(self) -> Iterable[Graph]:
        tracer: DefinitionTracer = DefinitionTracer(self._internal_modules)
        for item in self._items:
            origin, origin_type = item.trace_origin()
            self._graph.add_node(
                GraphNode(
                    origin,
                    origin,
                    'Python Class',
                    name=item.name,
                    origin=origin_type,
                    abstract=item.facts.get('abstract', False),
                    protocol=item.facts.get('protocol', False)
                )
            )
            for superclass in item.facts.get('superclass', []):
                module, name = superclass.rsplit('.', 1)
                superclass = tracer.trace(module, name)
                superclass_origin = tracer.origin_type(superclass)
                self._graph.add_node(
                    GraphNode(
                        superclass,
                        superclass,
                        'Python Class',
                        name=superclass.rsplit('.', 1)[-1],
                        origin=superclass_origin,
                        abstract=False,
                        protocol=False
                    )
                )
                self._graph.connect_nodes(origin, superclass)
        yield self._graph
