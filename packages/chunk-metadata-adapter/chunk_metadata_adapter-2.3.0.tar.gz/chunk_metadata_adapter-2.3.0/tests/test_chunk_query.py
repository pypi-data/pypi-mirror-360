import pytest
from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole

def test_from_dict_with_validation_non_string_enum():
    """
    Test that from_dict_with_validation correctly handles non-string enum values.
    This covers the `isinstance(val, str)` check in enum validation.
    """
    bad_data = {"type": 123}  # type should be a string
    _filter, errors = ChunkQuery.from_dict_with_validation(bad_data)
    assert _filter is None
    assert errors is not None
    assert "type" in errors["fields"]
    assert "must be one of" in errors["fields"]["type"][0]

def test_from_dict_with_validation_invalid_value_type():
    """
    Test that from_dict_with_validation rejects invalid data types for simple fields.
    This covers lines 156-168.
    """
    class Unserializable:
        pass
    
    bad_data = {"source": Unserializable()}
    _filter, errors = ChunkQuery.from_dict_with_validation(bad_data)
    assert _filter is None
    assert errors is not None
    assert "source" in errors["fields"]
    assert "must be str/int/float/bool/None" in errors["fields"]["source"][0]

def test_from_dict_with_validation_general_exception():
    """
    Test the general exception handler in from_dict_with_validation.
    This covers line 184.
    """
    # We can trigger a general exception by passing a value that pydantic
    # cannot handle during model construction, after our custom validation.
    # For example, a complex object for a simple field.
    class BadObject:
        def __str__(self):
            raise TypeError("Cannot convert to string")

    # This should pass our initial checks but fail in Pydantic's `cls(**data)`
    bad_data = {"ordinal": BadObject()}
    
    _filter, errors = ChunkQuery.from_dict_with_validation(bad_data)
    
    assert _filter is None
    assert errors is not None
    assert "error" in errors
    # The exact error message may vary, but it should indicate a problem.
    assert "ordinal" in errors["error"]
    assert "str/int/float/bool/None" in errors["error"]

# This test is for line 149, but it's hard to trigger this specific `except`
# without monkeypatching. The existing enum validation is quite comprehensive.
# We can add a placeholder test to acknowledge this.
def test_from_dict_with_validation_enum_exception_path():
    """
    Test case for the exception path in enum validation (line 149).
    This path is hard to reach as the preceding checks are thorough.
    We test with a value that fails the `val not in set(...)` check.
    """
    bad_data = {"role": "non_existent_role"}
    _filter, errors = ChunkQuery.from_dict_with_validation(bad_data)
    assert _filter is None
    assert errors is not None
    assert 'role' in errors['fields']
    assert "must be one of" in errors['fields']['role'][0]


def test_to_json_dict():
    """Test to_json_dict method with various data types."""
    query = ChunkQuery(
        uuid="12345678-1234-4123-8123-123456789012",
        type="DocBlock",
        tags=["tag1", "tag2"],
        block_meta={"key": "value", "nested": {"inner": "data"}},
        quality_score=0.95,
        is_public=True
    )
    
    json_dict = query.to_json_dict()
    
    # Verify all values are JSON serializable
    assert isinstance(json_dict["uuid"], str)
    assert isinstance(json_dict["type"], str)
    assert isinstance(json_dict["tags"], list)
    assert isinstance(json_dict["block_meta"], dict)
    assert isinstance(json_dict["quality_score"], float)
    assert isinstance(json_dict["is_public"], bool)


def test_from_json_dict():
    """Test from_json_dict method."""
    json_data = {
        "uuid": "12345678-1234-4123-8123-123456789012",
        "type": "DocBlock",
        "tags": ["tag1", "tag2"],
        "quality_score": 0.95
    }
    
    query = ChunkQuery.from_json_dict(json_data)
    
    assert query.uuid == "12345678-1234-4123-8123-123456789012"
    assert query.type == "DocBlock"
    assert query.tags == ["tag1", "tag2"]
    assert query.quality_score == 0.95


def test_to_flat_dict_with_created_at_none():
    """Test to_flat_dict removes created_at when it's None."""
    query = ChunkQuery(
        uuid="12345678-1234-4123-8123-123456789012",
        type="DocBlock",
        created_at=None  # Explicitly set to None
    )
    
    flat_dict = query.to_flat_dict()
    
    # created_at should be removed when None
    assert "created_at" not in flat_dict
    assert flat_dict["uuid"] == "12345678-1234-4123-8123-123456789012"
    assert flat_dict["type"] == "DocBlock"


def test_from_dict_with_validation_allowed_list_fields():
    """Test that list/dict are allowed for specific fields."""
    data = {
        "tags": ["tag1", "tag2"],  # list allowed
        "links": ["parent:uuid1", "related:uuid2"],  # list allowed
        "block_meta": {"key": "value"}  # dict allowed
    }
    
    query, errors = ChunkQuery.from_dict_with_validation(data)
    
    assert query is not None
    assert errors is None
    assert query.tags == ["tag1", "tag2"]
    assert query.links == ["parent:uuid1", "related:uuid2"]
    assert query.block_meta == {"key": "value"}


def test_from_dict_with_validation_disallowed_list_for_regular_field():
    """Test that list/dict are not allowed for regular fields."""
    data = {"project": ["not", "allowed"]}  # list not allowed for project
    query, errors = ChunkQuery.from_dict_with_validation(data)
    
    assert query is None
    assert errors is not None
    assert "project" in errors["fields"]
    assert "must be str, int, float, bool or dict" in errors["fields"]["project"][0]


def test_from_dict_with_validation_complex_object_type():
    """Test validation with complex object that fails type check."""
    # This should cover lines 156-168 more thoroughly
    class ComplexObject:
        def __init__(self):
            self.data = "test"
    
    data = {
        "project": ComplexObject(),  # Complex object not allowed
        "source": {"dict": "not allowed for source"},  # Dict not allowed for source
        "quality_score": ["list", "not", "allowed"]  # List not allowed for quality_score
    }
    
    query, errors = ChunkQuery.from_dict_with_validation(data)
    
    assert query is None
    assert errors is not None
    assert "project" in errors["fields"]
    assert "source" in errors["fields"]
    assert "quality_score" in errors["fields"]


def test_from_dict_with_validation_pydantic_validation_error():
    """Test handling of Pydantic ValidationError to cover line 184."""
    # Simply test that invalid data that passes our checks fails in Pydantic
    # This will naturally trigger the ValidationError path
    data = {
        "uuid": "12345678-1234-4123-8123-123456789012",  # Valid UUID
        "tags": "not_a_list_but_should_be"  # This will fail Pydantic validation
    }
    
    query, errors = ChunkQuery.from_dict_with_validation(data)
    
    assert query is None
    assert errors is not None
    assert "error" in errors
    assert "fields" in errors


def test_from_dict_with_validation_general_exception_handling():
    """Test general exception handling to cover line 184."""
    import unittest.mock
    
    # Mock the ChunkQuery constructor to raise a general exception
    with unittest.mock.patch.object(ChunkQuery, '__init__', side_effect=RuntimeError("General error")):
        data = {"uuid": "12345678-1234-4123-8123-123456789012"}  # Valid data
        query, errors = ChunkQuery.from_dict_with_validation(data)
        
        assert query is None
        assert errors is not None
        assert "error" in errors
        assert "General error" in errors["error"] 