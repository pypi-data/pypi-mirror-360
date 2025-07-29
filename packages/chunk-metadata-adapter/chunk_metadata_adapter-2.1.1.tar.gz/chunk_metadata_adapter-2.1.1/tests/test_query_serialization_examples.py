"""
Тесты для query_serialization_examples.py - компактное покрытие.
"""

import pytest
from chunk_metadata_adapter.query_serialization_examples import (
    example_query_serialization,
    example_dynamic_query_building,
    example_optimization_patterns,
    example_error_handling_patterns,
    example_query_composition
)
from chunk_metadata_adapter.chunk_query import ChunkQuery


class TestQuerySerializationExamples:
    """Компактные тесты для query_serialization_examples.py"""

    def test_example_query_serialization(self):
        """Тест сериализации запросов."""
        result = example_query_serialization()
        assert isinstance(result, dict)
        assert 'original' in result
        assert 'flat_dict' in result
        assert 'json_dict' in result
        assert isinstance(result['original'], ChunkQuery)

    def test_example_dynamic_query_building(self):
        """Тест динамического построения запросов."""
        result = example_dynamic_query_building()
        assert isinstance(result, list)
        assert len(result) == 3
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_example_optimization_patterns(self):
        """Тест паттернов оптимизации."""
        result = example_optimization_patterns()
        assert isinstance(result, list)
        assert len(result) == 4
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_example_error_handling_patterns(self):
        """Тест обработки ошибок."""
        result = example_error_handling_patterns()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_example_query_composition(self):
        """Тест композиции запросов."""
        result = example_query_composition()
        assert isinstance(result, list)
        assert len(result) == 3
        for query in result:
            assert isinstance(query, ChunkQuery)

    def test_all_functions_execute_without_errors(self):
        """Тест, что все функции выполняются без ошибок."""
        functions = [
            example_query_serialization,
            example_dynamic_query_building,
            example_optimization_patterns,
            example_error_handling_patterns,
            example_query_composition
        ]
        
        for func in functions:
            result = func()
            assert result is not None 