"""
Tests for the examples module (part 2).
"""
import re
import uuid
import pytest
from datetime import datetime, timezone

from chunk_metadata_adapter import (
    SemanticChunk, 
    ChunkType,
    ChunkRole,
    ChunkStatus
)
from chunk_metadata_adapter.examples import (
    example_basic_flat_metadata,
    example_structured_chunk,
    example_conversion_between_formats,
    example_chain_processing
)


class TestExamples:
    """Tests for the examples module functions."""
    
    def test_example_conversion_between_formats(self):
        """Test the conversion between formats example."""
        # Run the example
        result = example_conversion_between_formats()
        
        # Verify the result structure
        assert "original" in result
        assert "flat" in result
        assert "restored" in result
        
        # Verify the original is a SemanticChunk
        assert isinstance(result["original"], SemanticChunk)
        
        # Verify the flat is a dictionary
        assert isinstance(result["flat"], dict)
        
        # Verify the restored is a SemanticChunk
        assert isinstance(result["restored"], SemanticChunk)
        
        # Verify the UUIDs match
        assert result["original"].uuid == result["flat"]["uuid"]
        assert result["original"].uuid == result["restored"].uuid
        
        # Verify the types match
        assert result["original"].type == ChunkType.COMMENT
        assert result["flat"]["type"] == "Comment"
        assert result["restored"].type == ChunkType.COMMENT
        
        # Verify the roles match
        assert result["original"].role == ChunkRole.REVIEWER
        assert result["flat"]["role"] == "reviewer"
        assert result["restored"].role == ChunkRole.REVIEWER
        
        # Verify the text matches
        assert result["original"].text == result["flat"]["text"]
        assert result["original"].text == result["restored"].text
        
    def test_example_chain_processing(self):
        """Test the chain processing example."""
        # Run the example
        results = example_chain_processing()
        
        # Verify we have 4 chunks
        assert len(results) == 4
        
        # Verify all chunks are SemanticChunk instances
        for chunk in results:
            assert isinstance(chunk, SemanticChunk)
        
        # Verify they all have the same source_id
        source_id = results[0].source_id
        for chunk in results:
            assert chunk.source_id == source_id
        
        # Verify the first chunk is the title
        assert results[0].summary == "Title"
        assert results[0].status == ChunkStatus.RAW
        
        # Verify chunks 1-3 have links to the title chunk
        for i in range(1, 4):
            assert any(link.endswith(results[0].uuid) for link in results[i].links)
            assert results[i].status == ChunkStatus.INDEXED
        
        # Verify all chunks have the correct metrics
        for chunk in results:
            assert chunk.metrics.quality_score == 0.95
            assert chunk.metrics.used_in_generation is True
            assert chunk.metrics.matches == 3
            assert chunk.metrics.feedback.accepted == 2
            
        # Verify the correct ordinals
        for i, chunk in enumerate(results):
            assert chunk.ordinal == i 