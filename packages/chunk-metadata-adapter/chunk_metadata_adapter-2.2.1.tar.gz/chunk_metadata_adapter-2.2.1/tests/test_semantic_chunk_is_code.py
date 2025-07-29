"""
Tests for is_code functionality in SemanticChunk.
Tests for is_code method, is_code_chunk field, and code detection logic.
"""
import pytest
import uuid
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, LanguageEnum

def valid_uuid():
    return str(uuid.uuid4())

def test_semantic_chunk_is_code():
    """Test the is_code method of SemanticChunk."""
    # Test CODE_BLOCK type always returns True
    code_chunk = SemanticChunk(
        body="def hello(): pass",
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.UNKNOWN  # Even with unknown language
    )
    assert code_chunk.is_code() is True
    
    # Test programming language with non-code type
    python_chunk = SemanticChunk(
        body="def hello(): pass",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.PYTHON
    )
    assert python_chunk.is_code() is True
    
    # Test natural language
    text_chunk = SemanticChunk(
        body="This is just text",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN
    )
    assert text_chunk.is_code() is False
    
    # Test unknown language with non-code type
    unknown_chunk = SemanticChunk(
        body="Some content",
        type=ChunkType.MESSAGE,
        language=LanguageEnum.UNKNOWN
    )
    assert unknown_chunk.is_code() is False
    
    # Test various programming languages
    programming_languages = [
        LanguageEnum.PYTHON, LanguageEnum.JAVASCRIPT, LanguageEnum.JAVA,
        LanguageEnum.C, LanguageEnum.CPP, LanguageEnum.CSHARP, LanguageEnum.GO,
        LanguageEnum.RUST, LanguageEnum.TYPESCRIPT, LanguageEnum.PHP,
        LanguageEnum.RUBY, LanguageEnum.SWIFT, LanguageEnum.KOTLIN,
        LanguageEnum.SCALA, LanguageEnum.HASKELL, LanguageEnum.ASSEMBLY,
        LanguageEnum.SHELL, LanguageEnum.SQL, LanguageEnum.HTML, LanguageEnum.CSS,
        LanguageEnum.JSON, LanguageEnum.XML, LanguageEnum.YAML, LanguageEnum.ONEC
    ]
    
    for lang in programming_languages:
        chunk = SemanticChunk(
            body="some code",
            type=ChunkType.DOC_BLOCK,
            language=lang
        )
        assert chunk.is_code() is True, f"Language {lang} should be detected as code"
    
    # Test natural languages
    natural_languages = [
        LanguageEnum.EN, LanguageEnum.RU, LanguageEnum.UK, LanguageEnum.DE,
        LanguageEnum.FR, LanguageEnum.ES, LanguageEnum.ZH, LanguageEnum.JA
    ]
    
    for lang in natural_languages:
        chunk = SemanticChunk(
            body="some text",
            type=ChunkType.DOC_BLOCK,
            language=lang
        )
        assert chunk.is_code() is False, f"Language {lang} should not be detected as code"


def test_semantic_chunk_is_code_edge_cases():
    """Test edge cases for the is_code method."""
    # Test with None language
    chunk_none_lang = SemanticChunk(
        body="some content",
        type=ChunkType.DOC_BLOCK,
        language=None
    )
    assert chunk_none_lang.is_code() is False
    
    # Test CODE_BLOCK with natural language (should still be True)
    code_with_natural_lang = SemanticChunk(
        body="This is code documentation",
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.EN
    )
    assert code_with_natural_lang.is_code() is True
    
    # Test different chunk types with programming languages
    chunk_types = [ChunkType.MESSAGE, ChunkType.DRAFT, ChunkType.TASK, 
                   ChunkType.SUBTASK, ChunkType.TZ, ChunkType.COMMENT, 
                   ChunkType.LOG, ChunkType.METRIC]
    
    for chunk_type in chunk_types:
        chunk = SemanticChunk(
            body="print('hello')",
            type=chunk_type,
            language=LanguageEnum.PYTHON
        )
        assert chunk.is_code() is True, f"Chunk type {chunk_type} with Python should be detected as code"


def test_semantic_chunk_is_code_integration():
    """Integration test for is_code method with ChunkMetadataBuilder."""
    from chunk_metadata_adapter import ChunkMetadataBuilder
    
    builder = ChunkMetadataBuilder()
    source_id = str(uuid.uuid4())
    
    # Test building code chunk
    code_chunk = builder.build_semantic_chunk(
        body="def calculate(x, y):\n    return x + y",
        language=LanguageEnum.PYTHON,
        chunk_type=ChunkType.CODE_BLOCK,
        source_id=source_id,
        start=0,
        end=1
    )
    assert code_chunk.is_code() is True
    
    # Test building text chunk
    text_chunk = builder.build_semantic_chunk(
        body="This is a documentation paragraph explaining the function.",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        start=0,
        end=1
    )
    assert text_chunk.is_code() is False
    
    # Test building 1C code chunk
    onec_chunk = builder.build_semantic_chunk(
        body="Процедура ВыполнитьОперацию()\n    // 1С код\nКонецПроцедуры",
        language=LanguageEnum.ONEC,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        start=0,
        end=1
    )
    assert onec_chunk.is_code() is True


def test_is_code_field_automatic_computation():
    """Test that is_code_chunk field is automatically computed during chunk creation."""
    # Test 1: CODE_BLOCK type with natural language should be True
    chunk1 = SemanticChunk(
        body="This is a comment in English",
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.EN
    )
    assert chunk1.is_code_chunk is True
    
    # Test 2: Programming language with DOC_BLOCK type should be True
    chunk2 = SemanticChunk(
        body="def function(): pass",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.PYTHON
    )
    assert chunk2.is_code_chunk is True
    
    # Test 3: Natural language with DOC_BLOCK type should be False
    chunk3 = SemanticChunk(
        body="This is documentation text",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN
    )
    assert chunk3.is_code_chunk is False
    
    # Test 4: Unknown language with DOC_BLOCK should be False
    chunk4 = SemanticChunk(
        body="Some unknown content",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN
    )
    assert chunk4.is_code_chunk is False


def test_is_code_field_consistency_with_method():
    """Test that is_code_chunk field matches the is_code() method result."""
    test_cases = [
        (ChunkType.CODE_BLOCK, LanguageEnum.PYTHON, True),
        (ChunkType.CODE_BLOCK, LanguageEnum.EN, True),
        (ChunkType.DOC_BLOCK, LanguageEnum.JAVASCRIPT, True),
        (ChunkType.DOC_BLOCK, LanguageEnum.EN, False),
        (ChunkType.COMMENT, LanguageEnum.RUST, True),
        (ChunkType.COMMENT, LanguageEnum.RU, False),
        (ChunkType.DRAFT, LanguageEnum.ONEC, True),
        (ChunkType.DRAFT, LanguageEnum.UNKNOWN, False),
    ]
    
    for chunk_type, language, expected in test_cases:
        chunk = SemanticChunk(
            body="test content",
            type=chunk_type,
            language=language
        )
        
        # Both field and method should return the same value
        assert chunk.is_code_chunk == expected
        assert chunk.is_code() == expected
        assert chunk.is_code_chunk == chunk.is_code()


def test_is_code_field_with_builder():
    """Test is_code_chunk field when using ChunkMetadataBuilder."""
    from chunk_metadata_adapter import ChunkMetadataBuilder
    
    builder = ChunkMetadataBuilder(project="TestProject")
    
    # Test with code chunk
    code_chunk = builder.build_semantic_chunk(
        body="print('hello')",
        language=LanguageEnum.PYTHON,
        chunk_type=ChunkType.CODE_BLOCK,
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    assert code_chunk.is_code_chunk is True
    
    # Test with text chunk
    text_chunk = builder.build_semantic_chunk(
        body="This is documentation",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=str(uuid.uuid4()),
        start=0,
        end=1
    )
    assert text_chunk.is_code_chunk is False


def test_is_code_field_serialization():
    """Test that is_code_chunk field is properly serialized and deserialized."""
    # Create chunk with code
    original = SemanticChunk(
        body="function test() { return true; }",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.JAVASCRIPT
    )
    assert original.is_code_chunk is True
    
    # Test flat dict serialization
    flat_dict = original.to_flat_dict()
    assert flat_dict["is_code_chunk"] == "true"  # Should be string in flat format
    
    # Test deserialization
    restored = SemanticChunk.from_flat_dict(flat_dict)
    assert restored.is_code_chunk is True
    
    # Test JSON serialization
    json_dict = original.model_dump()
    assert json_dict["is_code_chunk"] is True
    
    # Test reconstruction from dict
    reconstructed = SemanticChunk(**json_dict)
    assert reconstructed.is_code_chunk is True


def test_is_code_field_edge_cases():
    """Test is_code_chunk field with edge cases."""
    # Test with None language
    chunk1 = SemanticChunk(
        body="test content",
        type=ChunkType.DOC_BLOCK,
        language=None
    )
    assert chunk1.is_code_chunk is False
    
    # Test with None is_code_chunk value (should be automatically computed)
    chunk2 = SemanticChunk(
        body="def test(): pass",
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.PYTHON,
        is_code_chunk=None  # Will be automatically computed
    )
    # Should be automatically computed as True
    assert chunk2.is_code_chunk is True
    
    # Test all programming languages return True
    for lang in [LanguageEnum.PYTHON, LanguageEnum.JAVASCRIPT, LanguageEnum.JAVA, 
                 LanguageEnum.CPP, LanguageEnum.RUST, LanguageEnum.GO, LanguageEnum.ONEC]:
        chunk = SemanticChunk(
            body="test code",
            type=ChunkType.DOC_BLOCK,
            language=lang
        )
        assert chunk.is_code_chunk is True, f"Language {lang} should be detected as code"
    
    # Test all natural languages return False (unless CODE_BLOCK type)
    for lang in [LanguageEnum.EN, LanguageEnum.RU, LanguageEnum.DE, LanguageEnum.FR]:
        chunk = SemanticChunk(
            body="test text",
            type=ChunkType.DOC_BLOCK,
            language=lang
        )
        assert chunk.is_code_chunk is False, f"Language {lang} should not be detected as code"


def test_is_code_field_validate_and_fill():
    """Test is_code_chunk field computation in validate_and_fill method."""
    # Test with minimal data
    data = {
        "body": "console.log('hello');",
        "type": "DocBlock",
        "language": "JavaScript"
    }
    
    chunk, errors = SemanticChunk.validate_and_fill(data)
    assert errors is None
    assert chunk is not None
    # Debug: check if JavaScript is detected as programming language
    assert LanguageEnum.is_programming_language(LanguageEnum.JAVASCRIPT) is True
    assert chunk.is_code_chunk is True
    
    # Test with natural language
    data2 = {
        "body": "This is English text",
        "type": "DocBlock", 
        "language": "en"
    }
    
    chunk2, errors2 = SemanticChunk.validate_and_fill(data2)
    assert errors2 is None
    assert chunk2 is not None
    assert chunk2.is_code_chunk is False 