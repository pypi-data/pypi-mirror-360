from collections.abc import Iterable, Sequence, Callable
from pathlib import Path

from bauklotz.business.filter import Filter
from bauklotz.business.pipe import Pipe
from bauklotz.business.pipe.graph import GraphPipe
from bauklotz.configuration.catalog import Catalog
from bauklotz.configuration.catalog.builtin import BuiltinCatalog
from bauklotz.configuration.dsl.tokenizer import Token, FilterToken, NameToken, ArgToken, StringToken, NumberToken, \
    FileContent, ConnectionToken, BooleanToken, InputChannelToken, ReportToken, LabeledConnectionTokenStart, \
    LabeledConnectionTokenEnd
from bauklotz.reporting.report import Report


class MortarParser:
    def __init__(
            self,
            tokens: Iterable[Token],
            catalog: Catalog = BuiltinCatalog(),
            create_pipe: Callable[[], Pipe] = GraphPipe,
            base_path: Path = Path()
    ):
        self._tokens: Sequence[Token] = tuple(tokens)
        self._catalog: Catalog = catalog
        self._index: int = 0
        self._pipe: Pipe = create_pipe()
        self._filters: dict[str, Filter] = dict()
        self._reporter: dict[str, Report] = dict()
        self._channels: set[str] = set()
        self._base_path: Path = base_path

    def get_result(self) -> Pipe:
        return self._pipe

    def parse(self) -> Pipe:
        while self._index < len(self._tokens):
            if self._peek() is NameToken:
                self._connection()
            elif self._peek() is FilterToken:
                self._filter()
            elif self._peek() is ReportToken:
                self._report()
            elif self._peek() is InputChannelToken:
                self._pipe.add_input_channel(self._channel())
            else:
                raise TypeError(f"Could not parse token {self._tokens[self._index]}")
        return self._pipe


    def _filter(self) -> None:
        self._consume(FilterToken)
        module: str = self._name()
        name: str = self._name()
        args: dict[str, str | int | float | Path] = self._arguments()
        filter_: Filter = self._catalog.build_filter(module, name, args)
        self._filters[filter_.name] = filter_
        self._pipe.add_filter(filter_)


    def _report(self) -> None:
        self._consume(ReportToken)
        module: str = self._name()
        name: str = self._name()
        args: dict[str, str | int | float | Path] = self._arguments()
        report: Report = self._catalog.build_report(module, name, args)
        self._reporter[report.name] = report
        self._pipe.add_report(report)

    def _channel(self) -> str:
        self._consume(InputChannelToken)
        name: str = self._name()
        self._channels.add(name)
        return name


    def _connection(self) -> None:
        print("Connection")
        source: str = self._name()
        print(self._tokens[0].content)
        print("Type", self._peek())
        if self._peek() is LabeledConnectionTokenStart:
            self._connection_with_label(source)
        else:
            self._connection_without_label(source)

    def _connection_without_label(self, source: str | None) -> str:
        if source is None:
            source = self._name()
        self._consume(ConnectionToken)
        target: str = self._name()
        self._connect(source, target, set())
        if self._peek() is ConnectionToken:
            return self._connection_without_label(target)
        if self._peek() is LabeledConnectionTokenStart:
            return self._connection_with_label(target)
        return target

    def _connection_with_label(self, source: str | None) -> str:
        self._labels: set[str] = set()
        if source is None:
            source = self._name()
        self._consume(LabeledConnectionTokenStart)
        while self._peek() is NameToken:
            self._labels.add(self._name())
        self._consume(LabeledConnectionTokenEnd)
        target: str = self._name()
        self._connect(source, target, self._labels)
        if self._peek() is ConnectionToken:
            return self._connection_without_label(target)
        if self._peek() is LabeledConnectionTokenStart:
            return self._connection_with_label(target)
        return target


    def _connect(self, src: str, target: str, labels: set[str]) -> None:
        if src in self._channels:
            self._pipe.wire(src, self._filters[target])
        if src in self._filters and target in self._filters:
            self._pipe.connect(self._filters[src], self._filters[target], labels)
        if src in self._filters and target in self._reporter:
            self._pipe.connect(self._filters[src], self._reporter[target], labels)


    def _follow_up_connection(self) -> str:
        if self._peek() is LabeledConnectionTokenEnd:
            self._consume(LabeledConnectionTokenEnd)
        else:
            self._consume(ConnectionToken)
        return self._name()

    def _arguments(self) -> dict[str, str | int | float | Path]:
        arguments: dict[str, str | int | float | Path] = dict()
        while self._peek() is ArgToken:
            arguments.update([self._argument()])
        return arguments

    def _argument(self) -> tuple[str, str | int | float | Path]:
        name: str = self._consume(ArgToken).content
        for possible_value in (self._boolean, self._string, self._number, self._file):
            try:
                return name, possible_value()
            except TypeError:
                continue
        raise TypeError(f"Could not parse argument {name}")

    def _name(self) -> str:
        return self._consume(NameToken).content

    def _string(self) -> str:
        return self._consume(StringToken).content

    def _number(self) -> float | int:
        return float(self._consume(NumberToken).content)

    def _boolean(self) -> bool:
        return bool(self._consume(BooleanToken))

    def _file(self) -> Path:
        file_path: str = self._consume(FileContent).content
        if Path(file_path).is_absolute():
            return Path(file_path)
        else:
            return self._base_path.joinpath(file_path)

    def _consume[T: Token](self, expected: type[T]) -> T:
        token = self._tokens[self._index]
        if not isinstance(token, expected):
            raise TypeError(f"Expected {expected.__name__} but got {token}.")
        else:
            self._index += 1
            return token

    def _peek(self) -> type[Token | None]:
        return type(self._tokens[self._index]) if self._index < len(self._tokens) else type(None)