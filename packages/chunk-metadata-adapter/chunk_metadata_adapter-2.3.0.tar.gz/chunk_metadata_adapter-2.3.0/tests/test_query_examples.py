"""
Тесты для query_examples.py - компактное покрытие основных функций.
"""

import pytest
from chunk_metadata_adapter.query_examples import (
    example_equality_queries,
    example_comparison_queries,
    example_range_queries,
    example_in_queries,
    example_enum_queries,
    example_validation_errors,
    example_complex_query,
    example_real_world_scenarios
)
from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.data_types import ChunkType, ChunkStatus, LanguageEnum


class TestQueryExamples:
    """Компактные тесты для query_examples.py"""

    def test_example_equality_queries(self):
        """Тест запросов на равенство."""
        result = example_equality_queries()
        assert isinstance(result, ChunkQuery)
        assert result.project == "MyProject"

    def test_example_comparison_queries(self):
        """Тест запросов сравнения."""
        result = example_comparison_queries()
        assert isinstance(result, ChunkQuery)
        assert result.feedback_accepted == ">5"

    def test_example_range_queries(self):
        """Тест диапазонных запросов."""
        result = example_range_queries()
        assert isinstance(result, ChunkQuery)
        assert result.feedback_accepted == "[1,10]"

    def test_example_in_queries(self):
        """Тест IN запросов."""
        result = example_in_queries()
        assert isinstance(result, ChunkQuery)
        assert "in:" in result.project

    def test_example_enum_queries(self):
        """Тест enum запросов."""
        result = example_enum_queries()
        assert isinstance(result, ChunkQuery)
        assert result.block_type is not None

    def test_example_validation_errors(self):
        """Тест валидации ошибок."""
        errors = example_validation_errors()
        assert isinstance(errors, dict)
        assert 'fields' in errors

    def test_example_complex_query(self):
        """Тест комплексного запроса."""
        result = example_complex_query()
        assert isinstance(result, ChunkQuery)
        assert result.type == ChunkType.DOC_BLOCK.value
        assert result.language == LanguageEnum.PYTHON.value

    def test_example_real_world_scenarios(self):
        """Тест реальных сценариев."""
        result = example_real_world_scenarios()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_all_functions_execute_without_errors(self):
        """Тест, что все функции выполняются без ошибок."""
        functions = [
            example_equality_queries,
            example_comparison_queries,
            example_range_queries,
            example_in_queries,
            example_enum_queries,
            example_validation_errors,
            example_complex_query,
            example_real_world_scenarios
        ]
        
        for func in functions:
            result = func()
            assert result is not None 