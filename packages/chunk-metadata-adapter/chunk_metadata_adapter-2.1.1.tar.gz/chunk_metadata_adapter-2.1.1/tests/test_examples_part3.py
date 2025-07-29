import pytest
from chunk_metadata_adapter.examples import (
    example_filter_factory_method,
    example_filter_usage
)
from chunk_metadata_adapter.chunk_query import ChunkQuery

def test_example_filter_factory_method(capsys):
    """
    Test the example_filter_factory_method function.
    This test captures stdout and verifies the output and return values.
    """
    filter_obj, errors, filter_obj2, errors2 = example_filter_factory_method()

    # Check the first (valid) filter
    assert isinstance(filter_obj, ChunkQuery)
    assert errors is None
    assert filter_obj.type == "DocBlock"
    assert filter_obj.start == '>100'
    assert filter_obj.year == 'in:2022,2023'

    # Check the second (invalid) filter
    assert filter_obj2 is None
    assert isinstance(errors2, dict)
    assert 'fields' in errors2 and 'start' in errors2['fields']

    # Check captured output
    captured = capsys.readouterr()
    assert "Filter created:" in captured.out
    assert "Validation errors:" in captured.out

def test_example_filter_usage(capsys):
    """
    Test the example_filter_usage function.
    This test captures stdout and verifies the output and return values.
    """
    f1, f2, flat, f2_restored, err3, filtered = example_filter_usage()

    # Verify the created filters
    assert isinstance(f1, ChunkQuery)
    assert f1.type == "DocBlock"
    assert isinstance(f2, ChunkQuery)
    assert f2.start == '>=10'

    # Verify serialization and deserialization
    assert isinstance(flat, dict)
    assert 'start' in flat
    assert isinstance(f2_restored, ChunkQuery)
    assert f2_restored.start == f2.start

    # Verify validation error
    assert isinstance(err3, dict)
    assert 'fields' in err3 and 'start' in err3['fields']

    # Verify the simple filtering example
    assert isinstance(filtered, list)
    assert len(filtered) == 2
    assert filtered[0]['type'] == 'DocBlock' and filtered[0]['start'] == 15
    assert filtered[1]['type'] == 'DocBlock' and filtered[1]['start'] == 50

    # Check captured output
    captured = capsys.readouterr()
    assert "Filter (equality):" in captured.out
    assert "Filter (comparison/in):" in captured.out
    assert "Flat filter:" in captured.out
    assert "Restored from flat:" in captured.out
    assert "Validation error:" in captured.out
    assert "Filtered chunks:" in captured.out 