import pytest
import enum
from chunk_metadata_adapter.utils import to_flat_dict

class MyEnum(enum.Enum):
    A = "a"
    B = "b"

def test_array_with_str():
    data = {"arr": ["a", "b", "c"]}
    flat = to_flat_dict(data, for_redis=False)
    assert flat["arr"] == ["a", "b", "c"]

def test_array_with_int():
    data = {"arr": [1, 2, 3]}
    flat = to_flat_dict(data, for_redis=False)
    assert flat["arr"] == [1, 2, 3]

def test_array_with_float():
    data = {"arr": [1.1, 2.2, 3.3]}
    flat = to_flat_dict(data, for_redis=False)
    assert flat["arr"] == [1.1, 2.2, 3.3]

def test_array_with_bool():
    data = {"arr": [True, False, True]}
    flat = to_flat_dict(data, for_redis=False)
    assert flat["arr"] == [True, False, True]

def test_array_with_enum():
    data = {"arr": [MyEnum.A, MyEnum.B]}
    flat = to_flat_dict(data, for_redis=False)
    assert flat["arr"] == ["a", "b"]

def test_array_with_mixed_valid_types():
    data = {"arr": [1, "x", 2.5, False, MyEnum.B]}
    flat = to_flat_dict(data, for_redis=False)
    assert flat["arr"] == [1, "x", 2.5, False, "b"]

def test_array_with_dict_should_fail():
    data = {"arr": [1, {"x": 2}]}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False)

def test_array_with_list_should_fail():
    data = {"arr": [1, [2, 3]]}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False)

def test_array_with_tuple_should_fail():
    data = {"arr": [1, (2, 3)]}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False)

def test_array_with_set_should_fail():
    data = {"arr": [1, {2, 3}]}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False)

def test_array_with_object_should_fail():
    class Dummy:
        pass
    data = {"arr": [1, Dummy()]}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False)

def test_array_with_nested_array_should_fail():
    data = {"arr": [1, [2, [3]]]}  # вложенный список
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False) 