"""
Tests to improve coverage of all modules to 90%+
Focuses on uncovered lines identified by coverage report.
"""
import pytest
import uuid
from chunk_metadata_adapter.metadata_builder import ChunkMetadataBuilder
from chunk_metadata_adapter.semantic_chunk import SemanticChunk, ChunkMetrics
from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus

def valid_uuid():
    return str(uuid.uuid4())

def test_metadata_builder_invalid_source_id():
    """Test invalid source_id validation"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_flat_metadata(
            body="test",
            source_id="invalid-uuid",
            ordinal=0,
            type=ChunkType.DOC_BLOCK,
            language="en"
        )

def test_metadata_builder_invalid_coverage():
    """Test coverage validation"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="coverage must be a float in"):
        builder.build_flat_metadata(
            body="test",
            source_id=valid_uuid(),
            ordinal=0,
            type=ChunkType.DOC_BLOCK,
            language="en",
            coverage="invalid"
        )

def test_metadata_builder_invalid_link_parent():
    """Test invalid link_parent validation"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_flat_metadata(
            body="test",
            source_id=valid_uuid(),
            ordinal=0,
            type=ChunkType.DOC_BLOCK,
            language="en",
            link_parent="invalid-uuid"
        )

def test_metadata_builder_invalid_link_related():
    """Test invalid link_related validation"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_flat_metadata(
            body="test",
            source_id=valid_uuid(),
            ordinal=0,
            type=ChunkType.DOC_BLOCK,
            language="en",
            link_related="invalid-uuid"
        )

def test_metadata_builder_invalid_tags():
    """Test invalid tags type"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="tags must be a list of strings or None"):
        builder.build_flat_metadata(
            body="test",
            source_id=valid_uuid(),
            ordinal=0,
            type=ChunkType.DOC_BLOCK,
            language="en",
            tags="not_a_list"
        )

def test_metadata_builder_coverage_out_of_range():
    """Test coverage out of range"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="coverage must be in"):
        builder.build_flat_metadata(
            body="test",
            source_id=valid_uuid(),
            ordinal=0,
            type=ChunkType.DOC_BLOCK,
            language="en",
            coverage=2.0
        )

def test_metadata_builder_semantic_chunk_invalid_source_id():
    """Test semantic chunk invalid source_id"""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DOC_BLOCK,
            source_id="invalid-uuid"
        )

def test_metadata_builder_semantic_chunk_invalid_links():
    """Test semantic chunk invalid links"""
    builder = ChunkMetadataBuilder()
    
    # Invalid link format
    with pytest.raises(ValueError, match="Link must follow 'relation:uuid' format"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DOC_BLOCK,
            links=["invalid_format"]
        )
    
    # Invalid UUID in link
    with pytest.raises(ValueError, match="Invalid UUID4 in link"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DOC_BLOCK,
            links=["parent:invalid-uuid"]
        )

def test_metadata_builder_semantic_chunk_invalid_types():
    """Test semantic chunk invalid types"""
    builder = ChunkMetadataBuilder()
    
    # Invalid tags type
    with pytest.raises(ValueError, match="tags must be a list of strings"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DOC_BLOCK,
            tags="not_a_list"
        )
    
    # Invalid links type
    with pytest.raises(ValueError, match="links must be a list of strings"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DOC_BLOCK,
            links="not_a_list"
        )

def test_metadata_builder_conversion_methods():
    """Test conversion methods"""
    builder = ChunkMetadataBuilder()
    
    # Test flat_to_semantic
    flat_data = builder.build_flat_metadata(
        body="test",
        source_id=valid_uuid(),
        ordinal=0,
        type=ChunkType.DOC_BLOCK,
        language="en"
    )
    
    chunk = builder.flat_to_semantic(flat_data)
    assert isinstance(chunk, SemanticChunk)
    
    # Test semantic_to_flat
    flat_result = builder.semantic_to_flat(chunk)
    assert isinstance(flat_result, dict)
    
    # Test json conversions
    json_dict = builder.semantic_to_json_dict(chunk)
    assert isinstance(json_dict, dict)
    
    restored = builder.json_dict_to_semantic(json_dict)
    assert isinstance(restored, SemanticChunk)

def test_metadata_builder_valid_str_method():
    """Test valid_str method in build_semantic_chunk"""
    builder = ChunkMetadataBuilder()
    
    # This will trigger the valid_str method for string fields
    chunk = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DOC_BLOCK,
        category="test",     # Valid string, should remain
        title="test_title",  # Valid string, should remain  
        source="test_source" # Valid string, should remain
    )
    
    assert chunk.category == "test"
    assert chunk.title == "test_title"
    assert chunk.source == "test_source"

def test_semantic_chunk_validate_and_fill_json_errors():
    """Test validate_and_fill JSON parsing errors"""
    # Invalid tags JSON
    data = {
        "body": "test",
        "tags": "invalid_json["
    }
    
    chunk, errors = SemanticChunk.validate_and_fill(data)
    assert chunk is None
    assert "tags" in errors["fields"]
    
    # Invalid block_meta JSON
    data2 = {
        "body": "test",
        "block_meta": "invalid_json["
    }
    
    chunk2, errors2 = SemanticChunk.validate_and_fill(data2)
    assert chunk2 is None
    assert "block_meta" in errors2["fields"]

def test_semantic_chunk_validate_and_fill_autofill():
    """Test validate_and_fill autofill logic"""
    data = {
        "body": "test",
        "type": ChunkType.DOC_BLOCK,  # Required field
        "chunking_version": None,     # Will get "1.0"
        "project": None,              # min_length=0 field  
        "ordinal": None,              # ge=0 field
        "quality_score": "",          # empty string for numeric
        "is_public": None,            # bool field
        "tags": None,                 # list field
        "year": None,                 # Will get 0, then None
    }
    
    chunk, errors = SemanticChunk.validate_and_fill(data)
    assert chunk is not None
    assert errors is None
    assert chunk.chunking_version == ""  # chunking_version заполняется как пустая строка для None
    assert chunk.project == ""
    assert chunk.ordinal == 0
    assert chunk.quality_score == 0.0
    assert chunk.is_public == False
    assert chunk.tags == []
    assert chunk.year is None

def test_semantic_chunk_model_post_init():
    """Test model_post_init edge cases"""
    # Test with dict metrics
    chunk = SemanticChunk(
        body="test",
        type=ChunkType.DOC_BLOCK,
        metrics={"quality_score": 0.8}
    )
    assert isinstance(chunk.metrics, ChunkMetrics)
    assert chunk.metrics.quality_score == 0.8
    
    # Test year normalization
    chunk3 = SemanticChunk(
        body="test",
        type=ChunkType.DOC_BLOCK,
        year=0
    )
    assert chunk3.year is None

def test_semantic_chunk_get_default_prop_val_error():
    """Test get_default_prop_val error case"""
    with pytest.raises(ValueError, match="No such property"):
        SemanticChunk.get_default_prop_val("invalid_property")

def test_semantic_chunk_from_flat_dict_complex():
    """Test from_flat_dict with complex scenarios"""
    # Test invalid JSON for non-tags fields
    flat_data = {
        'uuid': valid_uuid(),
        'source_id': valid_uuid(),
        'body': 'test',
        'type': 'DocBlock',
        'links': 'invalid_json['
    }
    
    with pytest.raises(ValueError, match="Field 'links' must be a list"):
        SemanticChunk.from_flat_dict(flat_data)

def test_chunk_query_validation_errors():
    """Test ChunkQuery validation errors"""
    invalid_data = {
        "start": {"invalid": "dict"},
        "quality_score": [1, 2, 3],
    }
    
    query, errors = ChunkQuery.from_dict_with_validation(invalid_data)
    assert errors is not None
    assert len(errors["fields"]) > 0

def test_chunk_query_various_types():
    """Test ChunkQuery with various data types"""
    data = {
        "uuid": valid_uuid(),
        "start": 100,              # int
        "quality_score": 0.8,      # float
        "is_public": True,         # bool
        "type": "DocBlock",        # str
        "ordinal": ">=5"           # str with operator
    }
    
    query, errors = ChunkQuery.from_dict_with_validation(data)
    assert query is not None
    assert errors is None
    assert query.start == 100
    assert query.quality_score == 0.8
    assert query.is_public == True
    assert query.type == "DocBlock"
    assert query.ordinal == ">=5"
 