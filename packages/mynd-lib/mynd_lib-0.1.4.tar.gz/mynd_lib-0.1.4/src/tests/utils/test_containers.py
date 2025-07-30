"""Unit tests for the mynds custom containers."""

import pytest

from mynd.utils.containers import Pair, Registry


# Tests for Pair class
def test_pair_creation():
    pair = Pair(1, 2)
    assert pair.first == 1
    assert pair.second == 2


def test_pair_immutability():
    pair = Pair("a", "b")
    with pytest.raises(AttributeError):
        pair.first = "c"


def test_pair_with_different_types():
    pair = Pair[object](1, "a")
    assert isinstance(pair.first, int)
    assert isinstance(pair.second, str)


# Tests for Registry class
@pytest.fixture
def sample_registry():
    registry = Registry[str, int]()
    registry.insert("one", 1)
    registry.insert("two", 2)
    registry.insert("three", 3)
    return registry


def test_registry_len(sample_registry):
    assert len(sample_registry) == 3
    assert sample_registry.count == 3


def test_registry_contains(sample_registry):
    assert "one" in sample_registry
    assert "four" not in sample_registry


def test_registry_getitem(sample_registry):
    assert sample_registry["two"] == 2
    with pytest.raises(KeyError):
        _ = sample_registry["four"]


def test_registry_setitem():
    registry = Registry[str, str]()
    registry["key"] = "value"
    assert registry["key"] == "value"


def test_registry_values(sample_registry):
    assert set(sample_registry.values) == {1, 2, 3}


def test_registry_keys(sample_registry):
    assert set(sample_registry.keys) == {"one", "two", "three"}


def test_registry_get(sample_registry):
    assert sample_registry.get("two") == 2
    assert sample_registry.get("four") is None
    assert sample_registry.get("four", 0) == 0


def test_registry_items(sample_registry):
    items = list(sample_registry.items())
    assert ("one", 1) in items
    assert ("two", 2) in items
    assert ("three", 3) in items


def test_registry_insert():
    registry = Registry[int, str]()
    registry.insert(1, "one")
    assert registry[1] == "one"


def test_registry_remove(sample_registry):
    sample_registry.remove("two")
    assert "two" not in sample_registry
    assert len(sample_registry) == 2


def test_registry_pop(sample_registry):
    value = sample_registry.pop("two")
    assert value == 2
    assert "two" not in sample_registry
    assert len(sample_registry) == 2


def test_registry_pop_nonexistent():
    registry = Registry[str, int]()
    with pytest.raises(KeyError):
        registry.pop("nonexistent")
