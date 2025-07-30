from pathlib import Path

from forgeschema import Schema


def test_path_expension():
    s = Schema(Path('test/data/test.x'), [Path('test/data/',)], ['x'])
    assert s.core_schema_path == Path('test/data/test.x')
    assert s.supporting_schemas_paths == [Path('test/data/test.x'), Path('test/data/inner1/test2.x'), Path('test/data/inner1/inner2/test3.x')]

    s = Schema(Path('test/data/test.x'), [Path('test/data/',)], ['x', 'y'])
    assert s.core_schema_path == Path('test/data/test.x')
    expected = [Path('test/data/test.x'), Path('test/data/test.y'),
                 Path('test/data/inner1/test2.y'), Path('test/data/inner1/test2.x'),
                 Path('test/data/inner1/inner2/test3.x'), Path('test/data/inner1/inner2/test3.y')]
    diff = set(s.supporting_schemas_paths) ^ set(expected)
    assert not diff
