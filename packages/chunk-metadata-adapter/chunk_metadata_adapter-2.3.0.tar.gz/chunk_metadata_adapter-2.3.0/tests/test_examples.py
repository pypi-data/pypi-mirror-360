"""
Tests for examples from the examples.py module.
"""
import uuid
import pytest
from chunk_metadata_adapter import (
    ChunkMetadataBuilder,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    SemanticChunk
)
from chunk_metadata_adapter.examples import (
    example_basic_flat_metadata,
    example_structured_chunk,
    example_conversion_between_formats,
    example_chain_processing,
    example_data_lifecycle,
    example_metrics_extension,
    example_full_chain_structured_semantic_flat,
    example_is_code_detection
)


def test_example_basic_flat_metadata():
    """Test the basic flat metadata example."""
    metadata = example_basic_flat_metadata()
    
    # Check that the example returns valid metadata
    assert isinstance(metadata, dict)
    assert "uuid" in metadata
    assert "sha256" in metadata
    assert "text" in metadata
    assert metadata["type"] == "CodeBlock"
    assert metadata["language"] == "Python"
    assert metadata["tags"] == "example,hello"


def test_example_structured_chunk():
    """Test the structured chunk example."""
    chunk = example_structured_chunk()
    
    # Check that the example returns a valid chunk
    assert isinstance(chunk, SemanticChunk)
    assert chunk.type == ChunkType.DOC_BLOCK
    assert chunk.language == "Markdown"
    assert chunk.summary == "Project introduction section"
    assert len(chunk.links) == 1
    assert chunk.links[0].startswith("parent:")


def test_example_conversion_between_formats():
    """Test the conversion between formats example."""
    result = example_conversion_between_formats()
    
    # Check that the example returns all expected components
    assert "original" in result
    assert "flat" in result
    assert "restored" in result
    
    # Check that conversions maintain integrity
    original = result["original"]
    flat = result["flat"]
    restored = result["restored"]
    
    assert original.uuid == restored.uuid
    assert original.text == restored.text
    assert original.type == restored.type


def test_example_chain_processing():
    """Test the chain processing example."""
    chunks = example_chain_processing()
    
    # Check that the example returns a list of chunks
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    
    # Check chunk relationships and processing
    title_chunk = chunks[0]
    assert title_chunk.ordinal == 0
    
    # Check that all other chunks point to the title
    for i in range(1, len(chunks)):
        child_chunk = chunks[i]
        assert any(link.startswith(f"parent:{title_chunk.uuid}") for link in child_chunk.links)
        assert child_chunk.status == ChunkStatus.INDEXED
        
    # Check metrics were updated
    for chunk in chunks:
        assert chunk.metrics.quality_score is not None
        assert chunk.metrics.used_in_generation is True
        assert chunk.metrics.matches is not None
        assert chunk.metrics.feedback.accepted > 0


def test_example_data_lifecycle():
    """Test the data lifecycle example."""
    result = example_data_lifecycle()
    
    # Check that all lifecycle stages are present
    assert "raw" in result
    assert "cleaned" in result
    assert "verified" in result
    assert "validated" in result
    assert "reliable" in result
    
    # Check the progression of statuses
    assert result["raw"].status == ChunkStatus.RAW
    assert result["cleaned"].status == ChunkStatus.CLEANED
    assert result["verified"].status == ChunkStatus.VERIFIED
    assert result["validated"].status == ChunkStatus.VALIDATED
    assert result["reliable"].status == ChunkStatus.RELIABLE
    
    # Check that all chunks have the same UUID (representing the same data evolving)
    uuid = result["raw"].uuid
    for stage in ["cleaned", "verified", "validated", "reliable"]:
        assert result[stage].uuid == uuid
    
    # Check that the text was corrected (fixed typo)
    assert "eample.com" in result["raw"].text
    assert "example.com" in result["cleaned"].text
    
    # Check that verification tags were added
    assert "verified_email" in result["verified"].tags
    
    # Check that validation added references
    assert any(link.startswith("reference:") for link in result["validated"].links)
    
    # Check that reliable data has a quality score
    assert result["reliable"].metrics.quality_score is not None
    assert result["reliable"].metrics.quality_score > 0.9


def test_example_metrics_extension():
    """Test the metrics extension example."""
    chunk = example_metrics_extension()
    assert isinstance(chunk, SemanticChunk)
    assert chunk.metrics.coverage == 0.95
    assert chunk.metrics.cohesion == 0.8
    assert chunk.metrics.boundary_prev == 0.7
    assert chunk.metrics.boundary_next == 0.9
    assert chunk.metrics.feedback.accepted == 0
    assert chunk.metrics.quality_score is None or 0 <= chunk.metrics.quality_score <= 1


def test_example_full_chain_structured_semantic_flat():
    """Test the full chain structured-semantic-flat example."""
    result = example_full_chain_structured_semantic_flat()
    assert "structured_dict" in result
    assert "semantic" in result
    assert "flat" in result
    assert "restored_semantic" in result
    assert "restored_dict" in result
    # Check equivalence of key fields
    assert result["restored_semantic"].body == result["structured_dict"]["body"]
    assert set(result["restored_semantic"].tags) == set(result["structured_dict"]["tags"])
    assert result["restored_semantic"].text == result["structured_dict"]["text"]
    assert result["restored_semantic"].type == result["structured_dict"]["chunk_type"]


def test_example_is_code_detection():
    """Test the is_code detection example."""
    examples = example_is_code_detection()
    
    # Verify we got 5 examples
    assert len(examples) == 5
    
    # Check specific examples
    python_example = examples[0][1]  # ("Python code", python_chunk)
    js_example = examples[1][1]      # ("JavaScript (DOC_BLOCK)", js_chunk)
    text_example = examples[2][1]    # ("English text", text_chunk)
    comment_example = examples[3][1] # ("Comment (CODE_BLOCK)", comment_chunk)
    onec_example = examples[4][1]    # ("1C code", onec_chunk)
    
    # Verify is_code detection
    assert python_example.is_code_chunk is True   # Python + CODE_BLOCK
    assert js_example.is_code_chunk is True       # JavaScript (programming language)
    assert text_example.is_code_chunk is False    # English + DOC_BLOCK
    assert comment_example.is_code_chunk is True  # CODE_BLOCK type (overrides language)
    assert onec_example.is_code_chunk is True     # 1C (programming language)
    
    # Verify consistency between method and field
    for name, chunk in examples:
        assert chunk.is_code_chunk == chunk.is_code(), f"Inconsistency in {name}"


def test_basic_flat_metadata_includes_is_code():
    """Test that basic flat metadata includes is_code_chunk field."""
    metadata = example_basic_flat_metadata()
    
    # Should include is_code_chunk field
    assert "is_code_chunk" in metadata
    # Should be True for Python code
    assert metadata["is_code_chunk"] == "true"  # String in flat format 