from typing import TypeAlias

PrimitiveType: TypeAlias = str | int | float | bool | None
JSONType: TypeAlias = PrimitiveType | list['JSONType'] | dict[str, 'JSONType']
