import uuid
import json
import pytest
from chunk_metadata_adapter import ChunkMetadataBuilder, SemanticChunk, ChunkType, ChunkRole, ChunkStatus, ChunkMetrics
from chunk_metadata_adapter.data_types import LanguageEnum
from datetime import datetime, timezone

def valid_uuid():
    return str(uuid.uuid4())

def valid_iso8601():
    return datetime.now(timezone.utc).isoformat()

def test_full_cycle_all_fields_positive():
    builder = ChunkMetadataBuilder(project="FullFields", unit_id=valid_uuid())
    input_dict = {
        "uuid": valid_uuid(),
        "source_id": valid_uuid(),
        "project": "FullFields",
        "task_id": valid_uuid(),
        "subtask_id": valid_uuid(),
        "unit_id": valid_uuid(),
        "type": ChunkType.CODE_BLOCK.value,
        "role": ChunkRole.DEVELOPER.value,
        "language": LanguageEnum.RU.value,
        "body": "raw text",
        "text": "cleaned text",
        "summary": "summary text",
        "ordinal": 42,
        "sha256": "b"*64,
        "created_at": valid_iso8601(),
        "status": ChunkStatus.RELIABLE.value,
        "source_path": "src/file.py",
        "quality_score": 0.95,
        "coverage": 0.8,
        "cohesion": 0.7,
        "boundary_prev": 0.6,
        "boundary_next": 0.5,
        "used_in_generation": True,
        "feedback_accepted": 2,
        "feedback_rejected": 1,
        "start": 5,
        "end": 25,
        "category": "science",
        "title": "All Fields Test",
        "year": 2023,
        "is_public": False,
        "source": "external",
        "block_type": "paragraph",
        "chunking_version": "2.0",
        "block_id": valid_uuid(),
        "embedding": [0.1, 0.2, 0.3],
        "block_index": 3,
        "source_lines_start": 10,
        "source_lines_end": 20,
        "tags": ["test", "example"],
        "links": [f"parent:{valid_uuid()}", f"related:{valid_uuid()}"],
        "block_meta": {"author": "vasily", "reviewed": True},
        "metrics": {
            "quality_score": 0.95,
            "coverage": 0.8,
            "cohesion": 0.7,
            "boundary_prev": 0.6,
            "boundary_next": 0.5,
            "used_in_generation": True,
            "feedback": {"accepted": 2, "rejected": 1, "modifications": 0}
        }
    }
    # JSON roundtrip
    json_str = json.dumps(input_dict)
    received_dict = json.loads(json_str)
    chunk, err = SemanticChunk.validate_and_fill(received_dict)
    assert err is None, f"Validation error: {err}"
    flat = builder.semantic_to_flat(chunk)
    restored = builder.flat_to_semantic(flat)
    # Проверяем только те поля, которые были заданы в input_dict
    for key, val in input_dict.items():
        if key in ["metrics", "tags", "links", "block_meta", "embedding"]:
            continue
        # Метрики теперь только внутри metrics
        if key in ["quality_score", "coverage", "cohesion", "boundary_prev", "boundary_next", "used_in_generation", "feedback_accepted", "feedback_rejected", "tokens"]:
            # Проверяем только если есть metrics
            if hasattr(restored, "metrics") and restored.metrics is not None:
                assert getattr(restored.metrics, key, None) == val, f"Mismatch in metrics field {key}"
            continue
        assert getattr(restored, key, None) == val, f"Mismatch in field {key}"
    assert set(restored.tags) == set(input_dict["tags"])
    assert set(restored.links) == set(input_dict["links"])
    assert restored.block_meta == input_dict["block_meta"]
    # embedding не сохраняется в Redis (только метаданные), FAISS хранит векторы отдельно
    assert restored.embedding == []  # После round-trip через Redis embedding пустой
    # Проверяем метрики внутри metrics
    for m in ["quality_score", "coverage", "cohesion", "boundary_prev", "boundary_next", "used_in_generation"]:
        assert getattr(restored.metrics, m) == input_dict["metrics"][m]
    assert restored.metrics.feedback.accepted == input_dict["metrics"]["feedback"]["accepted"]
    assert restored.metrics.feedback.rejected == input_dict["metrics"]["feedback"]["rejected"]
    assert restored.metrics.feedback.modifications == input_dict["metrics"]["feedback"].get("modifications", 0)

def pytest_parametrize_invalid_cases():
    # (field, invalid_value, expected_error_substr)
    return [
        ("uuid", "not-a-uuid", "UUID"),
        ("type", "notatype", "type"),
        ("role", "notarole", "role"),
        ("language", "notalang", "language"),
        ("body", "", "at least 1 character"),
        ("sha256", "short", "sha256"),
        ("created_at", "notadate", "created_at"),
        ("status", "notastatus", "status"),
        ("quality_score", 2.0, "quality_score"),
        ("coverage", -0.1, "coverage"),
        ("cohesion", 1.5, "cohesion"),
        ("boundary_prev", -1, "boundary_prev"),
        ("boundary_next", 2, "boundary_next"),
        ("used_in_generation", "notabool", "used_in_generation"),
        ("feedback_accepted", -1, "feedback_accepted"),
        ("feedback_rejected", -2, "feedback_rejected"),
        ("start", -1, "start"),
        ("end", -5, "end"),
        ("category", "x"*100, "category"),
        ("title", "y"*300, "title"),
        ("year", 3000, "year"),
        ("is_public", "notabool", "is_public"),
        ("source", "z"*100, "source"),
        ("block_type", "notablocktype", "block_type"),
        ("chunking_version", "", "chunking_version"),
        ("block_id", "not-a-uuid", "block_id"),
        ("embedding", "notalist", "embedding"),
        ("block_index", -1, "block_index"),
        ("source_lines_start", -5, "source_lines_start"),
        ("source_lines_end", -10, "source_lines_end"),
        ("tags", "notalist", "tags"),
        ("links", "notalist", "links"),
        ("block_meta", "notadict", "block_meta"),
    ]

@pytest.mark.parametrize("field,invalid_value,expected_error", pytest_parametrize_invalid_cases())
def test_full_cycle_all_fields_negative(field, invalid_value, expected_error):
    builder = ChunkMetadataBuilder(project="FullFields", unit_id=valid_uuid())
    base_dict = {
        "uuid": valid_uuid(),
        "source_id": valid_uuid(),
        "project": "FullFields",
        "task_id": valid_uuid(),
        "subtask_id": valid_uuid(),
        "unit_id": valid_uuid(),
        "type": ChunkType.CODE_BLOCK.value,
        "role": ChunkRole.DEVELOPER.value,
        "language": LanguageEnum.RU.value,
        "body": "raw text",
        "text": "cleaned text",
        "summary": "summary text",
        "ordinal": 42,
        "sha256": "b"*64,
        "created_at": valid_iso8601(),
        "status": ChunkStatus.RELIABLE.value,
        "source_path": "src/file.py",
        "quality_score": 0.95,
        "coverage": 0.8,
        "cohesion": 0.7,
        "boundary_prev": 0.6,
        "boundary_next": 0.5,
        "used_in_generation": True,
        "feedback_accepted": 2,
        "feedback_rejected": 1,
        "start": 5,
        "end": 25,
        "category": "science",
        "title": "All Fields Test",
        "year": 2023,
        "is_public": False,
        "source": "external",
        "block_type": "paragraph",
        "chunking_version": "2.0",
        "block_id": valid_uuid(),
        "embedding": [0.1, 0.2, 0.3],
        "block_index": 3,
        "source_lines_start": 10,
        "source_lines_end": 20,
        "tags": ["test", "example"],
        "links": [f"parent:{valid_uuid()}", f"related:{valid_uuid()}"],
        "block_meta": {"author": "vasily", "reviewed": True},
        "metrics": {
            "quality_score": 0.95,
            "coverage": 0.8,
            "cohesion": 0.7,
            "boundary_prev": 0.6,
            "boundary_next": 0.5,
            "used_in_generation": True,
            "feedback": {"accepted": 2, "rejected": 1, "modifications": 0}
        }
    }
    base_dict[field] = invalid_value
    json_str = json.dumps(base_dict)
    received_dict = json.loads(json_str)
    chunk, err = SemanticChunk.validate_and_fill(received_dict)
    autofill_fields = {"type", "role", "language", "status", "block_type", "chunking_version"}
    if field in autofill_fields:
        assert chunk is not None, f"Expected autofill for field {field}, got error: {err}"
    else:
        assert chunk is None, f"Expected validation error for field {field}, got chunk: {chunk}"
        if field == "body":
            assert err is not None and "at least 1 character" in str(err), f"Expected error for {field}, got: {err}"
        else:
            assert err is not None and expected_error in str(err), f"Expected error for {field}, got: {err}" 