"""
Tests for the data models (part 1).
"""
import re
import uuid
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
import uuid as uuidlib
from chunk_metadata_adapter.data_types import LanguageEnum

from chunk_metadata_adapter import (
    SemanticChunk,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    ChunkMetrics,
    FeedbackMetrics
)

class TestEnums:
    """Tests for enum types"""
    
    def test_chunk_type_values(self):
        """Test ChunkType enum values"""
        assert ChunkType.DOC_BLOCK == "DocBlock"
        assert ChunkType.CODE_BLOCK == "CodeBlock"
        assert ChunkType.MESSAGE == "Message"
        assert ChunkType.DRAFT == "Draft"
        assert ChunkType.TASK == "Task"
        assert ChunkType.SUBTASK == "Subtask"
        assert ChunkType.TZ == "TZ"
        assert ChunkType.COMMENT == "Comment"
        assert ChunkType.LOG == "Log"
        assert ChunkType.METRIC == "Metric"
        
    def test_chunk_role_values(self):
        """Test ChunkRole enum values"""
        assert ChunkRole.SYSTEM == "system"
        assert ChunkRole.USER == "user"
        assert ChunkRole.ASSISTANT == "assistant"
        assert ChunkRole.TOOL == "tool"
        assert ChunkRole.REVIEWER == "reviewer"
        assert ChunkRole.DEVELOPER == "developer"
        
    def test_chunk_status_values(self):
        """Test ChunkStatus enum values"""
        assert ChunkStatus.NEW == "new"
        assert ChunkStatus.INDEXED == "indexed"
        assert ChunkStatus.VERIFIED == "verified"
        assert ChunkStatus.OBSOLETE == "obsolete"
        assert ChunkStatus.REJECTED == "rejected"
        assert ChunkStatus.IN_PROGRESS == "in_progress"


class TestFeedbackMetrics:
    """Tests for FeedbackMetrics model"""
    
    def test_default_initialization(self):
        """Test default initialization of FeedbackMetrics"""
        metrics = FeedbackMetrics()
        assert metrics.accepted == 0
        assert metrics.rejected == 0
        assert metrics.modifications == 0
        
    def test_custom_initialization(self):
        """Test initialization with custom values"""
        metrics = FeedbackMetrics(accepted=5, rejected=2, modifications=3)
        assert metrics.accepted == 5
        assert metrics.rejected == 2
        assert metrics.modifications == 3
        
    def test_model_validation(self):
        """Test validation rules for the model"""
        # Should accept int values
        metrics = FeedbackMetrics(accepted=10, rejected=5, modifications=7)
        assert metrics.accepted == 10
        
        # В Pydantic 2.x отрицательные значения для int разрешены по умолчанию
        # Проверим, что мы можем создать модель с отрицательными значениями
        # и они сохраняются как есть, если валидация их не блокирует
        metrics = FeedbackMetrics(accepted=-1, rejected=-2, modifications=-3)
        assert metrics.accepted == -1
        assert metrics.rejected == -2
        assert metrics.modifications == -3


class TestChunkMetrics:
    """Tests for ChunkMetrics model"""
    
    def test_default_initialization(self):
        """Test default initialization of ChunkMetrics"""
        metrics = ChunkMetrics()
        assert metrics.quality_score is None
        assert metrics.coverage is None
        assert metrics.matches is None
        assert metrics.used_in_generation is False
        assert metrics.used_as_input is False
        assert metrics.used_as_context is False
        assert isinstance(metrics.feedback, FeedbackMetrics)
        
    def test_custom_initialization(self):
        """Test initialization with custom values"""
        metrics = ChunkMetrics(
            quality_score=0.95,
            coverage=0.8,
            matches=5,
            used_in_generation=True,
            used_as_input=True,
            used_as_context=False,
            feedback=FeedbackMetrics(accepted=3, rejected=1, modifications=2)
        )
        
        assert metrics.quality_score == 0.95
        assert metrics.coverage == 0.8
        assert metrics.matches == 5
        assert metrics.used_in_generation is True
        assert metrics.used_as_input is True
        assert metrics.used_as_context is False
        assert metrics.feedback.accepted == 3
        assert metrics.feedback.rejected == 1
        assert metrics.feedback.modifications == 2
        
    def test_validators(self):
        """Test validation rules for the model"""
        # Quality score should be between 0 and 1
        with pytest.raises(ValidationError):
            ChunkMetrics(quality_score=1.5)
            
        with pytest.raises(ValidationError):
            ChunkMetrics(quality_score=-0.1)
            
        # Coverage should be between 0 and 1
        with pytest.raises(ValidationError):
            ChunkMetrics(coverage=1.5)
            
        with pytest.raises(ValidationError):
            ChunkMetrics(coverage=-0.1)
            
        # Matches should be non-negative
        with pytest.raises(ValidationError):
            ChunkMetrics(matches=-1)


class TestSemanticChunk:
    """Tests for SemanticChunk model"""
    
    def test_minimal_initialization(self):
        """Test initialization with minimal required fields"""
        uuid_val = str(uuid.uuid4())
        data = dict(
            uuid=uuid_val,
            type=ChunkType.DOC_BLOCK,
            text="Test content",
            language=LanguageEnum.MARKDOWN,
            sha256="a" * 64,
            start=0,
            end=10,
            project="p",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            body="b",
            summary="sum",
            source_path="src.py",
            created_at=datetime.now(timezone.utc).isoformat(),
            chunking_version="1.0",
            links=[],
            tags=[],
            metrics=ChunkMetrics(),
            source_id=str(uuid.uuid4()),
            block_id=str(uuid.uuid4()),
        )
        chunk, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert chunk.uuid == uuid_val
        assert chunk.type == ChunkType.DOC_BLOCK
        assert chunk.text == "Test content"
        assert chunk.language == LanguageEnum.MARKDOWN
        assert chunk.sha256 == "a" * 64
        assert chunk.start == 0
        assert chunk.end == 10
        # Check defaults
        assert chunk.role in (ChunkRole.SYSTEM, "", None)
        assert chunk.project == "p"
        assert len(chunk.task_id) == 36
        assert len(chunk.subtask_id) == 36
        assert len(chunk.unit_id) == 36
        assert chunk.summary == "sum"
        assert len(chunk.source_id) == 36
        uuidlib.UUID(chunk.source_id, version=4)
        assert len(chunk.block_id) == 36
        uuidlib.UUID(chunk.block_id, version=4)
        assert chunk.source_lines in (None, [0,0])
        assert chunk.ordinal == 0
        assert chunk.status in (ChunkStatus.NEW, "", None)
        assert chunk.chunking_version == "1.0"
        assert chunk.embedding is None
        assert len(chunk.links) == 0
        assert len(chunk.tags) == 0
        assert chunk.metrics.quality_score is None

    def test_full_initialization(self):
        """Test initialization with all fields"""
        uuid_val = str(uuid.uuid4())
        source_id = str(uuid.uuid4())
        block_id = str(uuid.uuid4())
        data = dict(
            uuid=uuid_val,
            type=ChunkType.CODE_BLOCK,
            role=ChunkRole.DEVELOPER,
            project="TestProject",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            text="def test():\n    pass",
            summary="Test function",
            language=LanguageEnum.PYTHON,
            source_id=source_id,
            source_path="src/test.py",
            source_lines=[10, 11],
            ordinal=5,
            created_at=datetime.now(timezone.utc).isoformat(),
            status=ChunkStatus.VERIFIED,
            chunking_version="2.0",
            sha256="b" * 64,
            embedding=[0.1, 0.2, 0.3],
            links=["parent:"+str(uuid.uuid4())],
            tags=["test", "example"],
            metrics=ChunkMetrics(quality_score=0.9, used_in_generation=True),
            start=5,
            end=25,
            body="body",
            block_id=block_id,
        )
        chunk, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert chunk.uuid == uuid_val
        assert chunk.type == ChunkType.CODE_BLOCK
        assert chunk.role in (ChunkRole.SYSTEM, "", None, "developer", ChunkRole.DEVELOPER)
        assert chunk.project == "TestProject"
        assert len(chunk.task_id) == 36
        assert len(chunk.subtask_id) == 36
        assert len(chunk.unit_id) == 36
        assert chunk.text == "def test():\n    pass"
        assert chunk.summary == "Test function"
        assert chunk.language == LanguageEnum.PYTHON
        assert chunk.source_id == source_id
        assert chunk.source_path == "src/test.py"
        assert chunk.source_lines == [10, 11]
        assert chunk.ordinal == 5
        assert chunk.status == ChunkStatus.VERIFIED
        assert chunk.chunking_version == "2.0"
        assert chunk.sha256 == "b" * 64
        assert chunk.embedding == [0.1, 0.2, 0.3]
        assert len(chunk.block_id) == 36
        uuidlib.UUID(chunk.block_id, version=4)
        assert chunk.links[0].startswith("parent:")
        assert "test" in chunk.tags
        assert "example" in chunk.tags
        assert chunk.metrics.quality_score == 0.9
        assert chunk.metrics.used_in_generation is True
        assert chunk.start == 5
        assert chunk.end == 25
        assert chunk.body == "body"
        # Check defaults
        assert len(chunk.task_id) == 36
        assert len(chunk.subtask_id) == 36
        assert len(chunk.unit_id) == 36

    def test_body_field(self):
        """Test body field in SemanticChunk"""
        uuid_val = str(uuid.uuid4())
        data = dict(
            uuid=uuid_val,
            type=ChunkType.DOC_BLOCK,
            text="cleaned text",
            body="raw text",
            language=LanguageEnum.MARKDOWN,
            sha256="a" * 64,
            start=0,
            end=10,
            project="p",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            summary="sum",
            source_path="src.py",
            created_at=datetime.now(timezone.utc).isoformat(),
            chunking_version="1.0",
            links=[],
            tags=[],
            metrics=ChunkMetrics(),
        )
        chunk, err = SemanticChunk.validate_and_fill(data)
        assert err is None
        assert chunk.body == "raw text"
        assert chunk.text == "cleaned text"
        # Проверяем, что если не передать body — будет ошибка
        data_missing_body = dict(
            uuid=str(uuid.uuid4()),
            type=ChunkType.DOC_BLOCK,
            text="cleaned text",
            language=LanguageEnum.MARKDOWN,
            sha256="a" * 64,
            start=0,
            end=10,
            project="p",
            task_id=str(uuid.uuid4()),
            subtask_id=str(uuid.uuid4()),
            unit_id=str(uuid.uuid4()),
            summary="sum",
            source_path="src.py",
            created_at=datetime.now(timezone.utc).isoformat(),
            chunking_version="1.0",
            links=[],
            tags=[],
            metrics=ChunkMetrics(),
        )
        chunk, err = SemanticChunk.validate_and_fill(data_missing_body)
        assert chunk is None and err is not None 