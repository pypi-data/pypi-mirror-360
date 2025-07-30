"""Module with generic custom containers."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional


T = TypeVar("T")


@dataclass(frozen=True)
class Pair(Generic[T]):
    """Class representing a pair of items of the same type."""

    first: T
    second: T

    def __iter__(self) -> Iterator:
        """Returns an iterator for the pair."""
        return iter((self.first, self.second))


Key = TypeVar("Key")
Value = TypeVar("Value")


@dataclass
class Registry(Generic[Key, Value]):
    """Generic registry class."""

    _items: dict[Key, Value] = field(default_factory=dict)

    def __len__(self) -> int:
        """Returns the number of items in the registry."""
        return len(self._items)

    def __contains__(self, key: Key) -> bool:
        """Returns the number of items in the registry."""
        return key in self._items

    def __getitem__(self, key: Key) -> Value:
        """Returns the value for the given key."""
        return self._items[key]

    def __setitem__(self, key: Key, value: Value) -> None:
        """Inserts a key value pair in the registry."""
        self._items[key] = value

    @property
    def count(self) -> int:
        """Returns the number of items in the registry."""
        return len(self)

    @property
    def values(self) -> list[Value]:
        """Returns the values for the registered items."""
        return list(self._items.values())

    @property
    def keys(self) -> list[Key]:
        """Returns the keys for the registered items."""
        return list(self._items.keys())

    def get(self, key: Key, default: Optional[Value] = None) -> Value:
        """Returns a value if it is in the registry, or the default value."""
        return self._items.get(key, default)

    def items(self) -> list[tuple[Key, Value]]:
        """Returns the items in the registry."""
        return self._items.items()

    def insert(self, key: Key, value: Value) -> None:
        """Insert a key value pair in the registry."""
        self._items[key] = value

    def remove(self, key: Key) -> None:
        """Removes a key value pair in the registry."""
        self._items.pop(key)

    def pop(self, key: Key) -> Value:
        """Insert a key value pair in the registry."""
        return self._items.pop(key)
