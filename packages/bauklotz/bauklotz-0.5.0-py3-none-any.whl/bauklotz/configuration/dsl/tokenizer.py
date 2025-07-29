from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Self


@dataclass
class Token:
    line: int
    column: int
    content: str

    def __len__(self) -> int:
        return len(self.content)


@dataclass
class FilterToken(Token):
    pass

@dataclass
class ConnectionToken(Token):
    pass

@dataclass
class LabeledConnectionTokenStart(Token):
    pass


@dataclass
class LabeledConnectionTokenEnd(Token):
    pass


@dataclass
class NumberToken(Token):
    pass

@dataclass
class StringToken(Token):
    pass

@dataclass
class ArgToken(Token):
    pass

@dataclass
class FileContent(Token):
    pass

@dataclass
class NameToken(Token):
    pass

@dataclass
class InputChannelToken(Token):
    pass

@dataclass
class ReportToken(Token):
    pass

@dataclass
class BooleanToken(Token):
    def __bool__(self) -> bool:
        return self.content in ("true", "yes")



class MortarTokenizer:
    def __init__(self, text: str):
        self._text = text
        self._line: int = 1
        self._column: int = 1
        self._position: int = 0
        self._buffer: list[str] = list()
        self._tokens: list[Token] = list()
        self._active_string: bool = False


    def _create_token(self):
        content: str = ''.join(self._buffer)
        if not content:
            return
        match content.lower():
            case "channel": self._tokens.append(InputChannelToken(self._line, self._column, content))
            case "filter": self._tokens.append(FilterToken(self._line, self._column, content))
            case "report": self._tokens.append(ReportToken(self._line, self._column, content))
            case "->": self._tokens.append(ConnectionToken(self._line, self._column, content))
            case "-[": self._tokens.append(LabeledConnectionTokenStart(self._line, self._column, content))
            case "]->": self._tokens.append(LabeledConnectionTokenEnd(self._line, self._column, content))
            case _: self._tokens.append(self._handle_terminal(content))
        self._buffer.clear()
        self._column += len(self._tokens[-1])


    def _handle_terminal(self, content: str) -> Token:
        if content.lower() in ("true", "false", "yes", "no"):
            return BooleanToken(self._line, self._column, content.lower())
        if content.isnumeric():
            return NumberToken(self._line, self._column, content)
        if content.startswith('"') and content.endswith('"'):
            return StringToken(self._line, self._column, content[1:-1])
        if content.endswith(":"):
            return ArgToken(self._line, self._column, content[:-1])
        if content.startswith("@"):
            return FileContent(self._line, self._column, content[1:])
        return NameToken(self._line, self._column, content)

    def _handle_whitespace(self, space: str) -> None:
        if self._active_string:
            self._buffer.append(space)
        elif self._buffer:
            self._create_token()
        self._update_position(space)

    def _update_position(self, symbol: str) -> None:
        self._column += 1
        if symbol == "\n":
            self._line += 1
            self._column = 1


    def _advance(self) -> None:

        symbol: str = self._text[self._position]
        if symbol.isspace():
            return self._handle_whitespace(symbol)
        if symbol == '"':
            return self._handle_quote()
        self._buffer.append(symbol)


    def _handle_quote(self) -> None:
        if self._text[self._position - 1] == "\\" and self._active_string:
            self._buffer.pop()
            self._buffer.append('"')
        else:
            self._buffer.append('"')
            self._active_string = not self._active_string

    def tokenize(self) -> Self:
        while self._position < len(self._text):
            self._advance()
            self._position += 1
        self._create_token()
        return self

    def __iter__(self) -> Iterator[Token]:
        if not self._tokens:
            self.tokenize()
        return iter(self._tokens)

