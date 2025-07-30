"""
Test round-trip conversion for SemanticChunk with Redis storage.

Tests the complete cycle:
1. Create SemanticChunk with embedding
2. Convert to flat dict for Redis (embedding should be excluded)
3. Convert back to SemanticChunk
4. Add embedding back (simulating separate FAISS storage)
5. Verify objects are identical
"""
import pytest
from typing import Union
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum, BlockType


class TestRoundTripRedis:
    """Test round-trip conversion with Redis storage simulation"""
    
    def test_round_trip_with_embedding(self, valid_uuid, valid_sha256, valid_embedding, 
                                       valid_iso_timestamp, sample_text):
        """
        Test complete round-trip cycle:
        SemanticChunk -> to_flat_dict(for_redis=True) -> from_flat_dict -> SemanticChunk
        """
        # 1. Create original SemanticChunk with all data including embedding
        original_data = {
            "uuid": valid_uuid,
            "source_id": valid_uuid,
            "task_id": valid_uuid,
            "subtask_id": valid_uuid,
            "unit_id": valid_uuid,
            "block_id": valid_uuid,
            "type": ChunkType.DOC_BLOCK,
            "role": ChunkRole.USER,
            "language": LanguageEnum.EN,
            "body": sample_text,
            "text": sample_text,
            "summary": "Test summary",
            "ordinal": 42,
            "sha256": valid_sha256,
            "created_at": valid_iso_timestamp,
            "status": ChunkStatus.VERIFIED,
            "source_path": "/test/path.txt",
            "quality_score": 0.85,
            "coverage": 0.92,
            "cohesion": 0.78,
            "boundary_prev": 0.65,
            "boundary_next": 0.71,
            "used_in_generation": True,
            "feedback_accepted": 5,
            "feedback_rejected": 1,
            "feedback_modifications": 2,
            "start": 100,
            "end": 200,
            "category": "programming",
            "title": "Test Function",
            "year": 2024,
            "is_public": True,
            "source": "user",
            "block_type": BlockType.PARAGRAPH,
            "chunking_version": "2.0",
            "block_index": 3,
            "source_lines_start": 10,
            "source_lines_end": 20,
            "tags": ["python", "test", "function"],
            "links": ["related:uuid-123", "parent:uuid-456"],
            "block_meta": {"author": "test_user", "version": "1.0"},
            "embedding": valid_embedding
        }
        
        original_chunk = SemanticChunk(**original_data)
        
        # 2. Convert to flat dict for Redis (embedding should be excluded)
        flat_dict = original_chunk.to_flat_dict(for_redis=True)
        
        # Verify embedding is NOT in Redis flat dict
        assert "embedding" not in flat_dict, "Embedding should be excluded for Redis storage"
        
        # Verify all other essential fields are present as strings
        assert flat_dict["uuid"] == valid_uuid
        assert flat_dict["type"] == ChunkType.DOC_BLOCK.value
        assert flat_dict["role"] == ChunkRole.USER.value
        assert flat_dict["language"] == LanguageEnum.EN.value
        assert flat_dict["body"] == sample_text
        assert flat_dict["quality_score"] == "0.85"  # Float converted to string
        assert flat_dict["used_in_generation"] == "true"  # Bool converted to string
        assert flat_dict["feedback_accepted"] == "5"  # Int converted to string
        assert isinstance(flat_dict["tags"], list)  # Lists stay as lists
        assert isinstance(flat_dict["links"], list)
        
        # 3. Convert back from flat dict to SemanticChunk
        restored_chunk = SemanticChunk.from_flat_dict(flat_dict)
        
        # 4. Normalize types according to Pydantic schema
        restored_chunk = self._normalize_types(restored_chunk)
        
        # 5. Add embedding back (simulating retrieval from FAISS)
        restored_chunk.embedding = valid_embedding
        
        # 6. Verify objects are identical (excluding computed properties)
        self._compare_chunks(original_chunk, restored_chunk)
    
    def test_round_trip_without_embedding(self, valid_uuid, valid_sha256, 
                                          valid_iso_timestamp, sample_text):
        """Test round-trip without embedding"""
        original_data = {
            "uuid": valid_uuid,
            "type": ChunkType.DRAFT,
            "body": sample_text,
            "sha256": valid_sha256,
            "created_at": valid_iso_timestamp,
            "tags": ["test"],
            "links": [],
            # No embedding
        }
        
        original_chunk = SemanticChunk(**original_data)
        flat_dict = original_chunk.to_flat_dict(for_redis=True)
        restored_chunk = SemanticChunk.from_flat_dict(flat_dict)
        restored_chunk = self._normalize_types(restored_chunk)
        
        # Both should have None or empty list embedding (from_flat_dict converts None to [])
        assert original_chunk.embedding is None
        assert restored_chunk.embedding == []  # from_flat_dict converts None to empty list
        
        self._compare_chunks(original_chunk, restored_chunk)
    
    def test_tags_and_links_always_lists(self, valid_uuid, sample_text):
        """Verify tags and links are always List[str] regardless of format"""
        # Test with various tag/link formats
        test_cases = [
            {"tags": ["a", "b", "c"], "links": ["rel:uuid1", "rel:uuid2"]},
            {"tags": [], "links": []},
            {"tags": None, "links": None},
        ]
        
        for case in test_cases:
            original_data = {
                "uuid": valid_uuid,
                "type": ChunkType.DRAFT,
                "body": sample_text,
                **case
            }
            
            original_chunk = SemanticChunk(**original_data)
            flat_dict = original_chunk.to_flat_dict(for_redis=True)
            restored_chunk = SemanticChunk.from_flat_dict(flat_dict)
            restored_chunk = self._normalize_types(restored_chunk)
            
            # Both should have lists (empty if None was provided)
            # Note: SemanticChunk may initialize None tags/links as None, but from_flat_dict converts to []
            orig_tags = original_chunk.tags if original_chunk.tags is not None else []
            orig_links = original_chunk.links if original_chunk.links is not None else []
            rest_tags = restored_chunk.tags if restored_chunk.tags is not None else []
            rest_links = restored_chunk.links if restored_chunk.links is not None else []
            
            assert isinstance(rest_tags, list)
            assert isinstance(rest_links, list)
            
            # Content should match
            assert orig_tags == rest_tags
            assert orig_links == rest_links
    
    def _normalize_types(self, chunk: SemanticChunk) -> SemanticChunk:
        """
        Normalize types according to Pydantic schema after restoration from flat dict.
        This handles cases where JSON serialization/deserialization changes types.
        """
        # Get current data
        data = chunk.model_dump()
        
        # Go through model fields and normalize types
        for field_name, field_info in SemanticChunk.model_fields.items():
            if field_name not in data:
                continue
                
            value = data[field_name]
            if value is None:
                continue
                
            # Get field type annotation
            field_type = field_info.annotation
            
            # Handle Optional types
            origin = getattr(field_type, '__origin__', None)
            if origin is Union:
                args = getattr(field_type, '__args__', ())
                non_none_types = [arg for arg in args if arg != type(None)]
                if non_none_types:
                    field_type = non_none_types[0]
            
            # Normalize based on type
            try:
                # Enum types
                if hasattr(field_type, '__mro__') and any('Enum' in base.__name__ for base in field_type.__mro__):
                    if isinstance(value, str):
                        # Try to create enum from string value
                        data[field_name] = field_type(value)
                    elif not isinstance(value, field_type):
                        data[field_name] = field_type(str(value))
                
                # String fields - keep as-is if already string from flat dict
                elif field_type == str:
                    if not isinstance(value, str):
                        data[field_name] = str(value)
                
                # Numeric fields
                elif field_type in (int, float):
                    if isinstance(value, str):
                        data[field_name] = field_type(value)
                    elif not isinstance(value, field_type):
                        data[field_name] = field_type(value)
                
                # Boolean fields
                elif field_type == bool:
                    if isinstance(value, str):
                        data[field_name] = value.lower() in ('true', '1', 'yes')
                    elif not isinstance(value, bool):
                        data[field_name] = bool(value)
                        
                # Dict fields - keep as-is for version flexibility
                elif field_type == dict:
                    # Don't modify dict contents to preserve version formats
                    pass
                    
                # List fields - keep as-is
                elif hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                    # Lists should already be properly handled by from_flat_dict
                    pass
                    
            except (ValueError, TypeError):
                # If conversion fails, keep original value
                pass
        
        # Create new instance with normalized data
        return SemanticChunk(**data)
    
    def _compare_chunks(self, original: SemanticChunk, restored: SemanticChunk):
        """Compare two SemanticChunk objects for equality"""
        # Compare all fields except metrics (which has special handling)
        exclude_fields = {"metrics"}
        
        original_dict = original.model_dump(exclude=exclude_fields)
        restored_dict = restored.model_dump(exclude=exclude_fields)
        
        # Handle None values (some fields might be None in one but empty in another)
        for key in original_dict:
            orig_val = original_dict[key]
            rest_val = restored_dict.get(key)
            
            # Special handling for list fields (tags, links, embedding)
            if key in ["tags", "links", "embedding"]:
                orig_list = orig_val if orig_val is not None else []
                rest_list = rest_val if rest_val is not None else []
                assert orig_list == rest_list, f"Mismatch in {key}: {orig_list} != {rest_list}"
            # Special handling for year (0 becomes None in restoration)
            elif key == "year":
                if orig_val == 0:
                    assert rest_val is None, f"Year 0 should become None, got {rest_val}"
                else:
                    assert orig_val == rest_val, f"Mismatch in {key}: {orig_val} != {rest_val}"
            # Special handling for dict fields (JSON can change types inside)
            elif key in ["block_meta"] and isinstance(orig_val, dict) and isinstance(rest_val, dict):
                # Compare as strings for version flexibility as mentioned by user
                assert set(orig_val.keys()) == set(rest_val.keys()), f"Keys mismatch in {key}"
                for k in orig_val.keys():
                    orig_item = str(orig_val[k]) if orig_val[k] is not None else None
                    rest_item = str(rest_val[k]) if rest_val[k] is not None else None
                    assert orig_item == rest_item, f"Mismatch in {key}.{k}: {orig_item} != {rest_item}"
            else:
                assert orig_val == rest_val, f"Mismatch in {key}: {orig_val} != {rest_val}"
        
        # Compare metrics separately if both have them
        if original.metrics and restored.metrics:
            assert original.metrics.model_dump() == restored.metrics.model_dump()
    
    def test_flat_dict_structure_for_redis(self, valid_uuid, sample_text, valid_embedding):
        """Test that flat dict for Redis has correct structure"""
        chunk = SemanticChunk(
            uuid=valid_uuid,
            type=ChunkType.DOC_BLOCK,
            body=sample_text,
            embedding=valid_embedding,
            tags=["test", "redis"],
            quality_score=0.95,
            is_public=True
        )
        
        flat_dict = chunk.to_flat_dict(for_redis=True)
        
        # All values should be strings except lists
        for key, value in flat_dict.items():
            if key in ["tags", "links"]:
                assert isinstance(value, list), f"{key} should be list, got {type(value)}"
            else:
                assert isinstance(value, str), f"{key} should be string, got {type(value)}: {value}"
        
        # Specific checks
        assert flat_dict["quality_score"] == "0.95"
        assert flat_dict["is_public"] == "true"
        assert flat_dict["type"] == ChunkType.DOC_BLOCK.value
        assert "embedding" not in flat_dict  # Should be excluded 