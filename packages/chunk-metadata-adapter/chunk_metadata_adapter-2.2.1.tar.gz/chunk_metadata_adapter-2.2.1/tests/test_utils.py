import pytest
import uuid
from chunk_metadata_adapter.utils import (
    ChunkId, EnumBase, is_empty_value, get_empty_value_for_type, get_valid_default_for_type, get_base_type, get_valid_default_for_field, semantic_to_flat_value, coerce_value_with_modifiers, autofill_enum_field, str_to_list, list_to_str, to_flat_dict, from_flat_dict
)
import enum
import json as _json
import datetime
import re
from chunk_metadata_adapter.chunk_query import ChunkQuery

# --- EnumBase тестовый класс ---
class EnumTest(EnumBase):
    A = "a"
    B = "b"
    C = "c"

class EnumNoneTest(EnumBase):
    @classmethod
    def default_value(cls):
        return None

# --- Тесты для ChunkId ---
def test_chunkid_valid_uuid():
    u = str(uuid.uuid4())
    cid = ChunkId.validate(u, None)
    assert isinstance(cid, str)
    assert uuid.UUID(cid, version=4)

def test_chunkid_default_value():
    assert ChunkId.default_value() == ChunkId.DEFAULT_VALUE
    assert uuid.UUID(ChunkId.default_value(), version=4)

def test_chunkid_zero_uuid():
    zero = "00000000-0000-0000-0000-000000000000"
    cid = ChunkId.validate(zero, None)
    assert cid == ChunkId.DEFAULT_VALUE
    assert is_empty_value(cid)

def test_chunkid_default_uuid():
    cid = ChunkId.validate(ChunkId.DEFAULT_VALUE, None)
    assert cid == ChunkId.DEFAULT_VALUE
    assert is_empty_value(cid)

def test_chunkid_is_default():
    cid = ChunkId(ChunkId.DEFAULT_VALUE)
    assert cid.is_default()
    cid2 = ChunkId(str(uuid.uuid4()))
    assert not cid2.is_default()

def test_chunkid_invalid_uuid():
    with pytest.raises(ValueError):
        ChunkId.validate("not-a-uuid", None)
    with pytest.raises(ValueError):
        # Не v4: третий блок не начинается с '4'
        ChunkId.validate("12345678-1234-1234-1234-1234567890ab", None)

def test_chunkid_none():
    assert ChunkId.validate(None, None) is None

def test_chunkid_uuid_instance():
    u = uuid.uuid4()
    cid = ChunkId.validate(u, None)
    assert isinstance(cid, str)
    assert uuid.UUID(cid, version=4)

# --- Тесты для is_empty_value ---
def test_is_empty_value_various():
    assert is_empty_value(None)
    assert is_empty_value("")
    assert is_empty_value([])
    assert is_empty_value({})
    assert is_empty_value(())
    assert is_empty_value("None")
    assert is_empty_value(ChunkId.DEFAULT_VALUE)
    assert not is_empty_value("some-value")
    assert not is_empty_value(str(uuid.uuid4()))

# --- Тесты для EnumBase ---
def test_enum_base_default_value():
    assert EnumTest.default_value() == EnumTest.A
    assert EnumNoneTest.default_value() is None

def test_enum_base_members():
    vals = list(EnumTest)
    assert EnumTest.A in vals
    assert EnumTest.B in vals
    assert EnumTest.C in vals

# --- Тесты для get_empty_value_for_type ---
def test_get_empty_value_for_type():
    assert get_empty_value_for_type(int) == 0
    assert get_empty_value_for_type(float) == 0
    assert get_empty_value_for_type(str) == ""
    assert get_empty_value_for_type(bool) is False
    assert get_empty_value_for_type(list) == []
    assert get_empty_value_for_type(dict) == {}
    assert get_empty_value_for_type(tuple) == ()
    assert get_empty_value_for_type(EnumTest) == EnumTest.A
    assert get_empty_value_for_type(type(None)) is None

# --- Тесты для get_valid_default_for_type ---
def test_get_valid_default_for_type():
    assert get_valid_default_for_type(int) == 0
    assert get_valid_default_for_type(float) == 0
    assert get_valid_default_for_type(str) == ""
    assert get_valid_default_for_type(bool) is False
    assert get_valid_default_for_type(list) == []
    assert get_valid_default_for_type(dict) == {}
    assert get_valid_default_for_type(tuple) == ()
    assert get_valid_default_for_type(EnumTest) == EnumTest.A
    assert get_valid_default_for_type(uuid.UUID, uuid_zero=True) == ChunkId.empty_uuid4()

# --- Тесты для автозаполнения Enum ---
def test_enum_autofill_optional():
    # Симуляция автозаполнения для Optional[Enum]
    val = EnumTest.default_value()
    assert val == EnumTest.A
    val_none = EnumNoneTest.default_value()
    assert val_none is None

# --- Тесты для автозаполнения ChunkId ---
def test_chunkid_autofill_optional():
    # Симуляция автозаполнения для Optional[ChunkId]
    val = ChunkId.default_value()
    assert val == ChunkId.DEFAULT_VALUE
    assert is_empty_value(val)

# --- Тесты для преобразования и сравнения ---
def test_chunkid_equality():
    val = ChunkId.default_value()
    assert val == ChunkId.DEFAULT_VALUE
    assert str(val) == ChunkId.DEFAULT_VALUE
    assert not (val == str(uuid.uuid4()))

# --- Граничные случаи ---
def test_chunkid_all_zeros_variants():
    from chunk_metadata_adapter.utils import ChunkId
    # UUID с разным количеством нулей и разделителей
    for v in [
        "00000000-0000-0000-0000-000000000000",
        "00000000-0000-4000-8000-000000000000",
    ]:
        cid = ChunkId.validate(v, None)
        # Проверяем только валидность UUID
        assert isinstance(cid, str) and len(cid) == 36

# --- Проверка, что ChunkId всегда валидирует дефолтное значение ---
def test_chunkid_default_value_always_valid():
    cid = ChunkId.validate(ChunkId.default_value(), None)
    assert cid == ChunkId.DEFAULT_VALUE
    assert is_empty_value(cid)

def test_get_base_type():
    from typing import Optional, Union, List
    assert get_base_type(int) is int
    assert get_base_type(Optional[int]) is int
    assert get_base_type(Union[int, None]) is int
    assert get_base_type(Union[str, int]) is str  # берёт первый
    assert get_base_type(List[int]) == List[int]

class DummyField:
    def __init__(self, name, annotation, min_length=None, pattern=None):
        self.name = name
        self.annotation = annotation
        self.min_length = min_length
        self.pattern = pattern

def test_get_valid_default_for_field_uuid():
    field = DummyField('uuid', str)
    val = get_valid_default_for_field(field)
    assert isinstance(val, str)
    assert len(val) == 36
    import uuid as uuidlib
    uuidlib.UUID(val)

def test_get_valid_default_for_field_str_min_length():
    field = DummyField('name', str, min_length=5)
    val = get_valid_default_for_field(field)
    assert val == 'xxxxx'

def test_get_valid_default_for_field_str():
    field = DummyField('name', str)
    val = get_valid_default_for_field(field)
    assert val == ''

def test_get_valid_default_for_field_list_min_length():
    field = DummyField('tags', list, min_length=3)
    val = get_valid_default_for_field(field)
    assert val == [None, None, None]

def test_get_valid_default_for_field_list():
    field = DummyField('tags', list)
    val = get_valid_default_for_field(field)
    assert val == []

def test_get_valid_default_for_field_other_types():
    field = DummyField('count', int)
    assert get_valid_default_for_field(field) == 0
    field = DummyField('flag', bool)
    assert get_valid_default_for_field(field) is False
    field = DummyField('data', dict)
    assert get_valid_default_for_field(field) == {}
    field = DummyField('tup', tuple)
    assert get_valid_default_for_field(field) == () 

def test_semantic_to_flat_value_and_coerce():
    class DummyField:
        def __init__(self, annotation, min_length=None, max_length=None, ge=None, le=None, decimal_places=None):
            self.annotation = annotation
            self.min_length = min_length
            self.max_length = max_length
            self.ge = ge
            self.le = le
            self.decimal_places = decimal_places
    # str
    f = DummyField(str, min_length=3, max_length=5)
    assert semantic_to_flat_value("a", f, "f") == "axx"
    assert semantic_to_flat_value("abcdef", f, "f") == "abcde"
    # int
    f = DummyField(int, ge=10, le=20)
    assert semantic_to_flat_value(5, f, "f") == 10
    assert semantic_to_flat_value(25, f, "f") == 20
    # float
    f = DummyField(float, ge=0.5, le=2.5, decimal_places=1)
    assert semantic_to_flat_value(0.1, f, "f") == 0.5
    assert semantic_to_flat_value(3.0, f, "f") == 2.5
    assert semantic_to_flat_value(1.234, f, "f") == 1.2
    # bool
    f = DummyField(bool)
    assert semantic_to_flat_value(None, f, "f") is False
    assert semantic_to_flat_value(True, f, "f") is True
    # list
    f = DummyField(list, min_length=2, max_length=3)
    assert semantic_to_flat_value(["a"], f, "f") == "a,None"
    assert semantic_to_flat_value(["a","b","c","d"], f, "f") == "a,b,c"
    # dict
    f = DummyField(dict)
    assert semantic_to_flat_value({"x":1,"y":2}, f, "meta") == "meta.x=1,meta.y=2"
    # coerce_value_with_modifiers
    f = DummyField(str, min_length=3, max_length=5)
    assert coerce_value_with_modifiers("a", f) == "axx"
    f = DummyField(int, ge=10, le=20)
    assert coerce_value_with_modifiers(5, f) == 10
    f = DummyField(float, ge=0.5, le=2.5, decimal_places=1)
    assert coerce_value_with_modifiers(0.1, f) == 0.5
    f = DummyField(bool)
    assert coerce_value_with_modifiers("yes", f) is True
    f = DummyField(list, min_length=2)
    assert coerce_value_with_modifiers(["a"], f) == ["a", None]
    # ChunkId
    from chunk_metadata_adapter.utils import ChunkId
    f = DummyField(ChunkId)
    assert coerce_value_with_modifiers(None, f) is None

def test_autofill_enum_field():
    class DummyEnum(EnumBase):
        A = "a"
        B = "b"
        @classmethod
        def default_value(cls):
            return cls.A
    assert autofill_enum_field(None, DummyEnum) is None
    assert autofill_enum_field("a", DummyEnum) == "a"
    assert autofill_enum_field("bad", DummyEnum) == "a"
    assert autofill_enum_field(DummyEnum.B, DummyEnum) == "b"

def test_str_to_list_and_list_to_str():
    assert str_to_list("a,b,c") == ["a","b","c"]
    assert str_to_list("") == []
    assert str_to_list(None) == []
    with pytest.raises(ValueError):
        str_to_list(["a","b"])
    assert list_to_str(["a","b"]) == "a,b"
    assert list_to_str([]) == ""
    with pytest.raises(ValueError):
        str_to_list(123)
    with pytest.raises(ValueError):
        list_to_str("abc")

def test_to_flat_dict_and_from_flat_dict_basic():
    class DummyEnum(enum.Enum):
        A = "a"
        B = "b"
    class DummyObj:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    data = {
        "a": {
            "b": {
                "c": ["c0", "c1"],
                "d": 123,
                "e": DummyEnum.A,
                "f": DummyObj(1, [2, 3]),
                "g": True,
                "h": None,
            }
        },
        "z": "str",
        "t": 42
    }
    # for_redis=False: None не сохраняется
    flat = to_flat_dict(data, for_redis=False)
    print("[DEBUG] flat:", flat)
    assert flat["a.b.c"] == ["c0", "c1"]  # list -> list
    assert flat["a.b.d"] == 123  # int as is
    assert flat["a.b.e"] == "a"  # enum.value
    assert flat["a.b.f.x"] == 1  # int as is
    assert flat["a.b.f.y"] == [2, 3]  # list -> list
    assert flat["a.b.g"] is True  # bool as is
    assert "a.b.h" not in flat  # None не сохраняется
    assert flat["z"] == "str"  # str as is
    assert flat["t"] == 42  # int as is
    # Обратное преобразование
    restored = from_flat_dict(flat)
    assert restored["a"]["b"]["c"] == ["c0", "c1"]
    assert restored["a"]["b"]["d"] == 123
    assert restored["a"]["b"]["e"] == 'a'
    assert restored["a"]["b"]["f"]["x"] == 1
    assert restored["a"]["b"]["f"]["y"] == [2, 3]
    assert restored["a"]["b"]["g"] is True
    assert "h" not in restored["a"]["b"]
    assert restored["z"] == 'str'
    assert restored["t"] == 42
    # for_redis=True: None не сохраняется, списки только строки
    flat_redis = to_flat_dict(data, for_redis=True)
    assert flat_redis["a.b.c"] == ["c0", "c1"]  # list -> list (строки)
    assert flat_redis["a.b.d"] == "123"  # int -> str в списке
    assert flat_redis["a.b.e"] == DummyEnum.A.value  # enum.value -> str в списке
    assert flat_redis["a.b.f.x"] == "1"  # int -> str в списке
    assert flat_redis["a.b.f.y"] == ["2", "3"]  # list -> list строк
    assert flat_redis["a.b.g"] == "true"  # bool -> str в списке
    assert "a.b.h" not in flat_redis
    assert flat_redis["z"] == "str"  # str в списке
    assert flat_redis["t"] == "42"  # int -> str в списке

def test_to_flat_dict_empty():
    assert to_flat_dict({}, for_redis=False) == {}

def test_from_flat_dict_empty():
    assert from_flat_dict({}) == {}

def test_from_flat_dict_json_edge_cases():
    # JSON string but not array/dict
    flat = {"x": '"justastring"', "y": '42'}
    restored = from_flat_dict(flat)
    assert flat["x"] == '"justastring"'
    assert restored["x"] == "justastring"
    assert restored["y"] == 42

def test_to_flat_dict_deep_nesting():
    data = {"a": {"b": {"c": {"d": {"e": [1, 2, {"f": "g"}]}}}}}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False)

def test_to_flat_dict_with_enum_and_object():
    class MyEnum(enum.Enum):
        A = "a"
        B = "b"
    class Dummy:
        def __init__(self):
            self.x = 1
            self.y = [2, 3]
    data = {
        "enum": MyEnum.A,
        "obj": Dummy(),
        "arr": [1, 2, 3],
        "nested": {"z": MyEnum.B}
    }
    flat = to_flat_dict(data, for_redis=False)
    assert flat["enum"] == "a"
    assert flat["obj.x"] == 1
    assert flat["obj.y"] == [2, 3]
    assert flat["arr"] == [1, 2, 3]
    assert flat["nested.z"] == "b"
    flat_redis = to_flat_dict(data, for_redis=True)
    assert flat_redis["enum"] == "a"
    assert flat_redis["obj.x"] == "1"
    assert flat_redis["obj.y"] == ["2", "3"]
    assert flat_redis["arr"] == ["1", "2", "3"]
    assert flat_redis["nested.z"] == "b"

def test_to_flat_dict_empty_and_types():
    assert to_flat_dict({}, for_redis=False) == {}
    assert from_flat_dict({}) == {}
    data = {"a": None, "b": True, "c": False, "d": 0, "e": "", "f": []}
    flat = to_flat_dict(data, for_redis=False)
    assert "a" not in flat
    assert flat["b"] is True
    assert flat["c"] is False
    assert flat["d"] == 0
    assert flat["e"] == ""
    assert flat["f"] == []
    flat_redis = to_flat_dict(data, for_redis=True)
    assert flat_redis["f"] == []
    restored = from_flat_dict(flat)
    assert "a" not in restored
    assert restored["b"] is True
    assert restored["c"] is False
    assert restored["d"] == 0
    assert restored["e"] == ""
    assert restored["f"] == []

def test_to_redis_dict_flattening():
    import datetime
    data = {
        'a': {'b': {'c': 1}},
        'x': [1, 2, {'y': 3}],
        't': (4, 5),
        'd': {'e': {'f': {'g': 'deep'}}},
    }
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=True)

def test_to_redis_dict_types():
    import enum, datetime
    class E(enum.Enum):
        A = 'a'
    now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    today = datetime.date(2024, 1, 2)
    data = {
        's': 'str',
        'i': 42,
        'f': 3.14,
        'b1': True,
        'b0': False,
        'n': None,
        'e': E.A,
        'dt': now,
        'date': today,
        'bytes': b'abc',
    }
    out = to_flat_dict(data, for_redis=True)
    assert out['s'] == 'str'
    assert out['i'] == '42'
    assert out['f'] == '3.14'
    assert out['b1'] == 'true'
    assert out['b0'] == 'false'
    assert 'n' not in out  # None не сериализуется
    assert out['e'] == 'a'
    assert out['dt'] == now.isoformat()
    assert out['date'] == today.isoformat()
    assert out['bytes'] == "b'abc'"


def test_to_redis_dict_created_at_autofill():
    import re, datetime
    # created_at отсутствует
    d1 = to_flat_dict({'foo': 1}, for_redis=True)
    assert 'created_at' in d1
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", d1['created_at'])
    # created_at есть — не перезаписывается
    now = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    d2 = to_flat_dict({'created_at': now, 'foo': 2}, for_redis=True)
    assert d2['created_at'] == now.isoformat()


def test_to_redis_dict_empty_and_edge():
    # Пустой dict
    out = to_flat_dict({}, for_redis=True)
    assert isinstance(out, dict)
    assert 'created_at' in out
    # Пустые значения
    data = {'a': '', 'b': None, 'c': [], 'd': {}}
    out = to_flat_dict(data, for_redis=True)
    assert out['a'] == ''
    assert 'b' not in out  # None не сериализуется
    assert out['c'] == []
    assert out['d'] == '{}'


def test_to_redis_dict_bool_variants():
    data = {'t1': True, 't2': 1, 't3': 'true', 'f1': False, 'f2': 0, 'f3': 'false'}
    out = to_flat_dict(data, for_redis=True)
    assert out['t1'] == 'true'
    assert out['f1'] == 'false'
    # 1 и 0 сериализуются как строки
    assert out['t2'] == '1'
    assert out['f2'] == '0'
    # строки остаются строками
    assert out['t3'] == 'true'
    assert out['f3'] == 'false'


def test_to_redis_dict_keys_are_str():
    data = {1: 'a', (2, 3): 'b', 'x': 1}
    out = to_flat_dict(data, for_redis=True)
    for k in out.keys():
        assert isinstance(k, str)


def test_to_redis_dict_no_side_effects():
    import copy
    data = {'a': {'b': 1}, 'l': [1, 2], 'n': None}
    orig = copy.deepcopy(data)
    _ = to_flat_dict(data, for_redis=True)
    assert data == orig 

def test_adapter_list_dict_roundtrip_for_redis():
    meta = {
        'embedding': [0.1, 0.2, 0.3],
        'tags': ['a', 'b'],
        'links': [{'url': 'http://example.com'}],
        'text': 'test',
    }
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(meta, for_redis=True)

def test_enum_round_trip_with_enums():
    import enum
    from chunk_metadata_adapter.utils import to_flat_dict, from_flat_dict
    class MyEnum(enum.Enum):
        A = "a"
        B = "b"
    data = {"enum": MyEnum.B, "x": 1}
    flat = to_flat_dict(data, for_redis=True)
    # Без enums — строка
    restored = from_flat_dict(flat)
    assert isinstance(restored["enum"], str)
    # С enums — Enum
    enums = {"enum": MyEnum}
    restored_enum = from_flat_dict(flat, enums=enums)
    assert isinstance(restored_enum["enum"], MyEnum)
    assert restored_enum["enum"] == MyEnum.B 

def test_from_flat_dict_bytes_and_enum_uuid_json():
    import enum
    from chunk_metadata_adapter.utils import to_flat_dict, from_flat_dict, ChunkId
    from chunk_metadata_adapter.data_types import LanguageEnum, ChunkType
    data = {
        "language": LanguageEnum.RU,
        "type": ChunkType.DRAFT,
        "uuid": ChunkId("c71080b8-1234-5678-9999-abcdefabcdef"),
        "embedding": [0.1, 0.2],
        "tags": ["a", "b"],
        "links": [],
        "block_meta": {"foo": 1},
        "feedback": {"accepted": 1},
        "none_field": None,
        "is_public": False,
    }
    # Redis-режим: embedding отсутствует
    flat = to_flat_dict(data, for_redis=True)
    flat_bytes = {k: v.encode() if isinstance(v, str) else v for k, v in flat.items()}
    restored = from_flat_dict(flat_bytes)
    assert isinstance(restored["language"], LanguageEnum)
    assert isinstance(restored["type"], ChunkType)
    assert isinstance(restored["uuid"], str)
    assert "embedding" not in restored  # embedding не сериализуется для Redis
    assert isinstance(restored["tags"], list)
    assert isinstance(restored["links"], list)
    assert isinstance(restored["block_meta"], dict)
    assert isinstance(restored["feedback"], dict)
    assert "none_field" not in restored
    assert restored["is_public"] == "false" or restored["is_public"] is False

    # Обычный режим: embedding сохраняется
    flat2 = to_flat_dict(data, for_redis=False)
    restored2 = from_flat_dict(flat2)
    assert "embedding" in restored2
    assert isinstance(restored2["embedding"], list)


def test_to_flat_dict_for_redis_types():
    """
    Проверяет, что после сериализации для Redis в результирующем словаре нет ни одного значения,
    отличного от str, list или dict. Для списков и словарей — рекурсивная проверка.
    """
    from chunk_metadata_adapter.utils import to_flat_dict
    data = {
        "a": 1,
        "b": 2.5,
        "c": True,
        "d": None,
        "e": "str",
        "f": ["x", "y"],
        "g": [1, 2, 3],
        "h": False,
        "i": {"k": "v", "n": 1},
        "embedding": [0.1, 0.2],
    }
    flat = to_flat_dict(data, for_redis=True)
    def check_value(val):
        if isinstance(val, str):
            return True
        elif isinstance(val, list):
            return all(check_value(x) for x in val)
        elif isinstance(val, dict):
            return all(check_value(v) for v in val.values())
        else:
            return False
    for k, v in flat.items():
        assert isinstance(v, (str, list, dict)), f"Key {k} has value of type {type(v)}: {v}"
        assert check_value(v), f"Key {k} contains nested value of invalid type: {v}"
    assert "embedding" not in flat

def test_from_flat_dict_fail_safe():
    from chunk_metadata_adapter.utils import from_flat_dict
    # Некорректные Enum/UUID — остаются строкой
    flat = {"language": "not_a_lang", "uuid": 123, "embedding": "[1,2]"}
    restored = from_flat_dict(flat)
    assert restored["language"] == "not_a_lang"
    assert restored["uuid"] == "123"
    assert restored["embedding"] == [1,2] 

def test_from_flat_dict_bytes_always_decoded_to_str():
    from chunk_metadata_adapter.utils import from_flat_dict
    # flat dict с bytes и str
    flat = {
        "a": b"hello",
        "b": "world",
        "c": b"[1,2,3]",
        "d": b"123",
    }
    restored = from_flat_dict(flat)
    # Все значения должны быть str или преобразованы далее (например, c — list)
    assert isinstance(restored["a"], str)
    assert isinstance(restored["b"], str)
    assert isinstance(restored["c"], list)  # '[1,2,3]' -> [1,2,3]
    assert isinstance(restored["d"], int) or isinstance(restored["d"], str)
    # Проверяем, что именно строки, а не bytes
    for v in restored.values():
        if isinstance(v, str):
            assert not isinstance(v, bytes) 

def test_to_flat_dict_invalid_array_element():
    data = {"arr": [1, {"x": 2}]}
    with pytest.raises(ValueError, match="Invalid element in array at"):
        to_flat_dict(data, for_redis=False) 

def test_flat_dict_redis_scalar_and_list():
    from chunk_metadata_adapter.utils import to_flat_dict
    data = {
        "a": {"b": 123},
        "c": [0, 1, 2, 3, 4, 5],
        "d": "hello",
        "e": True,
        "f": 3.14,
    }
    flat = to_flat_dict(data, for_redis=True)
    assert flat["a.b"] == "123"
    assert flat["c"] == ["0", "1", "2", "3", "4", "5"]
    assert flat["d"] == "hello"
    assert flat["e"] == "true"
    assert flat["f"] == "3.14"

    # Проверка ошибки на вложенные коллекции в списке
    data_bad = {"x": [1, [2, 3], 4]}
    with pytest.raises(ValueError, match="Invalid element in array at x\\[1\\]"):
        to_flat_dict(data_bad, for_redis=True) 

def test_to_flat_dict_with_filter_operators():
    # Проверяем, что вложенные dict с операторами $gte/$lte/$in не разворачиваются
    data = {
        "score": {"$gte": 2, "$lte": 4},
        "other_field": {"$in": ["a", "b"]},  # не tags, чтобы показать работу с операторами
        "plain": 123,
        "nested": {"x": {"$gt": 1, "$lt": 5}},
        "mix": {"a": 1, "b": {"$in": [1, 2]}}
    }
    flat = to_flat_dict(data, for_redis=False)
    assert flat["score"] == {"$gte": 2, "$lte": 4}
    assert flat["other_field"] == {"$in": ["a", "b"]}
    assert flat["plain"] == 123
    assert flat["nested.x"] == {"$gt": 1, "$lt": 5}
    assert flat["mix.a"] == 1
    assert flat["mix.b"] == {"$in": [1, 2]} 

def test_chunk_query_to_flat_dict_with_operators():
    # Фильтр с вложенными операторами
    data = {
        "score": {"$gte": 2, "$lte": 4},
        "tags": ["a", "b"],  # tags должен быть списком строк
        "plain": 123,
        "nested": {"x": {"$gt": 1, "$lt": 5}},
        "mix": {"a": 1, "b": {"$in": [1, 2]}}
    }
    q = ChunkQuery(**data)
    flat = q.to_flat_dict(for_redis=False)
    assert flat["score"] == {"$gte": 2, "$lte": 4}
    assert flat["tags"] == ["a", "b"]  # список остается списком
    assert flat["plain"] == 123
    assert flat["nested.x"] == {"$gt": 1, "$lt": 5}
    assert flat["mix.a"] == 1
    assert flat["mix.b"] == {"$in": [1, 2]} 

def test_chunk_query_to_json_dict_unit():
    from chunk_metadata_adapter.chunk_query import ChunkQuery
    # Простой фильтр
    q = ChunkQuery(type="DocBlock", start={"$gte": 10}, tags=["a", "b"], plain=123)
    d = q.to_json_dict()
    assert isinstance(d, dict)
    assert d["type"] == "DocBlock"
    assert d["start"] == {"$gte": 10}
    assert d["tags"] == ["a", "b"]
    assert d["plain"] == 123
    # Проверяем сериализуемость
    import json
    json_str = json.dumps(d)
    assert isinstance(json_str, str)


def test_chunk_query_from_json_dict_unit():
    from chunk_metadata_adapter.chunk_query import ChunkQuery
    d = {"type": "DocBlock", "start": {"$gte": 10}, "tags": ["a", "b"], "plain": 123}
    q = ChunkQuery.from_json_dict(d)
    assert isinstance(q, ChunkQuery)
    assert q.type == "DocBlock"
    assert q.start == {"$gte": 10}
    assert q.tags == ["a", "b"]
    assert q.plain == 123


def test_chunk_query_json_integration():
    from chunk_metadata_adapter.chunk_query import ChunkQuery
    import json
    # 1. Создать экземпляр
    q1 = ChunkQuery(type="DocBlock", start={"$gte": 10}, tags=["a", "b"], plain=123)
    # 2. Перевести в словарь
    d = q1.to_json_dict()
    # 3. Сериализовать и десериализовать через json
    d2 = json.loads(json.dumps(d))
    # 4. Из словаря создать экземпляр
    q2 = ChunkQuery.from_json_dict(d2)
    # 5. Проверить эквивалентность
    assert q2.type == q1.type
    assert q2.start == q1.start
    assert q2.tags == q1.tags
    assert q2.plain == q1.plain 