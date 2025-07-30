"""
Basic tests for SemanticChunk model.
Tests for basic functionality, validation, and factory methods.
"""
import pytest
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics, FeedbackMetrics
from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum, ChunkRole, ChunkStatus, BlockType
import pydantic
import hashlib

def test_semanticchunk_factory_valid():
    data = dict(
        chunk_uuid=str(uuid.uuid4()),
        type=ChunkType.DOC_BLOCK.value,
        text="test",
        language=LanguageEnum.EN,
        sha256="a"*64,
        created_at="2024-01-01T00:00:00+00:00",
        body="b",
        summary="s"
    )
    chunk = SemanticChunk.from_dict_with_autofill_and_validation(data)
    assert chunk.text == "test"
    assert chunk.body == "b"
    assert chunk.summary == "s"
    assert chunk.language == LanguageEnum.EN


def test_semanticchunk_factory_missing_required():
    with pytest.raises(pydantic.ValidationError) as e:
        SemanticChunk.from_dict_with_autofill_and_validation({})
    assert "[type=missing" in str(e.value)

def valid_uuid():
    return str(uuid.uuid4())

def valid_sha256():
    return "a" * 64

def valid_created_at():
    return datetime.now(timezone.utc).isoformat()

def test_json_and_dict_serialization():
    """
    Test to_dict, to_json, from_dict, and from_json methods.
    """
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="Test for serialization",
        text="Test for serialization",
        type=ChunkType.COMMENT
    )
    
    # to_dict and from_dict
    chunk_dict = chunk.model_dump()
    assert isinstance(chunk_dict, dict)
    assert chunk_dict['text'] == "Test for serialization"
    
    recreated_from_dict = SemanticChunk.model_validate(chunk_dict)
    assert recreated_from_dict.uuid == chunk.uuid
    assert recreated_from_dict.text == chunk.text

    # to_json and from_json
    chunk_json = chunk.model_dump_json()
    assert isinstance(chunk_json, str)
    
    recreated_from_json = SemanticChunk.model_validate_json(chunk_json)
    assert recreated_from_json.uuid == chunk.uuid
    assert recreated_from_json.text == chunk.text

def test_validate_and_fill_tags_links_processing():
    """
    Test the specific processing of tags and links in validate_and_fill.
    """
    data = {
        "uuid": valid_uuid(),
        "source_id": valid_uuid(),
        "body": "testing tags and links",
        "text": "testing tags and links",
        "type": "Comment",
        "tags": ["tag1", "tag2", "tag3"],
        "links": ["parent:d1b3e4f5-a1b2-4c3d-8e9f-a0b1c2d3e4f5"]
    }
    chunk, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert chunk is not None
    assert chunk.tags == ["tag1", "tag2", "tag3"]
    assert chunk.links == ["parent:d1b3e4f5-a1b2-4c3d-8e9f-a0b1c2d3e4f5"]

    # Test with lists
    data_list = {
        "uuid": valid_uuid(),
        "source_id": valid_uuid(),
        "body": "testing tags and links with lists",
        "text": "testing tags and links with lists",
        "type": "Comment",
        "tags": ["tag1", "tag2"],
        "links": ["related:d1b3e4f5-a1b2-4c3d-8e9f-a0b1c2d3e4f5"]
    }
    chunk_list, err_list = SemanticChunk.validate_and_fill(data_list)
    assert err_list is None
    assert chunk_list is not None
    assert chunk_list.tags == ["tag1", "tag2"]
    assert chunk_list.links == ["related:d1b3e4f5-a1b2-4c3d-8e9f-a0b1c2d3e4f5"]

def test_validate_and_fill_created_at_processing():
    """
    Test the specific processing of created_at in validate_and_fill.
    """
    # 1. Test autofill
    data_no_date = {
        "uuid": valid_uuid(), "source_id": valid_uuid(), "text": "t", "body": "b", "type": "Log"
    }
    chunk_no_date, err_no_date = SemanticChunk.validate_and_fill(data_no_date)
    assert err_no_date is None
    assert chunk_no_date is not None
    assert chunk_no_date.created_at is not None

    # 2. Test parsing from timestamp
    import time
    ts = int(time.time())
    date_from_ts = datetime.fromtimestamp(ts, tz=timezone.utc)
    date_str_from_ts = date_from_ts.isoformat()
    data_ts = {
        "uuid": valid_uuid(), "source_id": valid_uuid(), "text": "t", "body": "b", "type": "Log", "created_at": date_str_from_ts
    }
    chunk_ts, err_ts = SemanticChunk.validate_and_fill(data_ts)
    assert err_ts is None
    assert chunk_ts is not None
    assert str(date_from_ts.year) in chunk_ts.created_at

    # 3. Test parsing from string
    date_str = "2023-01-01T12:00:00Z"
    data_str = {
        "uuid": valid_uuid(), "source_id": valid_uuid(), "text": "t", "body": "b", "type": "Log", "created_at": date_str
    }
    chunk_str, err_str = SemanticChunk.validate_and_fill(data_str)
    assert err_str is None
    assert chunk_str is not None
    assert "2023" in chunk_str.created_at

def test_validate_and_fill_invalid_enum():
    """
    Test validate_and_fill with an invalid enum value that has a default.
    """
    data = {
        "uuid": valid_uuid(),
        "source_id": valid_uuid(),
        "body": "Test invalid enum",
        "type": "InvalidTypeValue"
    }
    chunk, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert chunk is not None
    assert chunk.type == ChunkType.default_value()

def test_chunk_metrics_feedback_properties():
    """Test feedback properties in ChunkMetrics."""
    # Test with specific values
    metrics_with_feedback = ChunkMetrics(feedback=FeedbackMetrics(accepted=1, rejected=2, modifications=3))
    assert metrics_with_feedback.feedback_accepted == 1
    assert metrics_with_feedback.feedback_rejected == 2
    assert metrics_with_feedback.feedback_modifications == 3

    # Test case for when default_factory is used
    metrics_with_default_feedback = ChunkMetrics()
    assert metrics_with_default_feedback.feedback_accepted == 0
    assert metrics_with_default_feedback.feedback_rejected == 0
    assert metrics_with_default_feedback.feedback_modifications == 0

    # Test case for when feedback is None, which is allowed by Optional[]
    metrics_with_none_feedback = ChunkMetrics(feedback=None)
    assert metrics_with_none_feedback.feedback_accepted is None
    assert metrics_with_none_feedback.feedback_rejected is None
    assert metrics_with_none_feedback.feedback_modifications is None

def test_semantic_chunk_init_with_source_lines():
    """Test SemanticChunk initialization with source_lines."""
    chunk = SemanticChunk(
        uuid=valid_uuid(),
        source_id=valid_uuid(),
        body="body",
        type=ChunkType.DOC_BLOCK,
        source_lines=[10, 20]
    )
    assert chunk.source_lines_start == 10
    assert chunk.source_lines_end == 20
    assert chunk.source_lines == [10, 20]

def test_get_default_prop_val():
    """Test get_default_prop_val method."""
    assert SemanticChunk.get_default_prop_val("tags") == []
    assert SemanticChunk.get_default_prop_val("links") == []
    with pytest.raises(ValueError):
        SemanticChunk.get_default_prop_val("non_existent_prop")

def test_source_lines_setter():
    """Test the source_lines setter."""
    chunk = SemanticChunk(uuid=valid_uuid(), source_id=valid_uuid(), body="body", type=ChunkType.DOC_BLOCK)
    chunk.source_lines = [5, 15]
    assert chunk.source_lines_start == 5
    assert chunk.source_lines_end == 15

    chunk.source_lines = None
    assert chunk.source_lines_start is None
    assert chunk.source_lines_end is None

def test_from_flat_dict_block_type_enum():
    """Test that from_flat_dict correctly converts block_type to enum"""
    flat_data = {
        "body": "Test body",
        "type": "DocBlock",
        "block_type": "paragraph"
    }
    chunk = SemanticChunk.from_flat_dict(flat_data)
    assert isinstance(chunk.block_type, BlockType)
    assert chunk.block_type == BlockType.PARAGRAPH 