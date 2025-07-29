from collections.abc import Iterable
from pathlib import Path
from typing import Self

from asteval import Interpreter

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.reporting.item import Item, Label
from bauklotz.reporting.types import JSONType


class ComplexLabelConfig(FilterConfig):
    def __init__(self, code: Path):
        with open(code) as src:
            self._code = src.read().strip()

    @property
    def code(self) -> str:
        return self._code

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        return cls(Path(data['code']))



class ComplexLabelFilter[I: Item](Filter[I, I, ComplexLabelConfig]):
    def __init__(self, name: str, config: ComplexLabelConfig):
        super().__init__(name, config)
        pass

    def process(self, item: I) -> Iterable[I]:
        interpreter: Interpreter = Interpreter()
        interpreter.symtable['facts'] = dict(item.facts.items())
        interpreter.symtable['labels'] = item.labels
        interpreter.symtable['item'] = item.serialize()
        interpreter(self.config.code)
        item.labels = Label(interpreter.symtable['labels'])
        yield item
