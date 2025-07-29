from pathlib import Path
from os import getenv
from pytest import raises

from forgeschema.helpers import expand_path



def test_path_expansion_notexisting():
    assert expand_path(Path('not_a_file'), "*.*") == [Path('not_a_file')]

def test_path_expansion_single_file():
    single_file = Path('test/data/test.x')
    r = expand_path(single_file, "blah")
    assert r == [single_file]

def test_path_expansion_dir_non_recursive():
    root_path = Path('test/data/')
    r = expand_path(root_path, "*.x", recursive=False)
    assert r == [Path('test/data/test.x')]
    r = expand_path(root_path, "*.y", recursive=False)
    assert r == [Path('test/data/test.y')]
    r = expand_path(root_path, "*.*", recursive=False)
    assert r == [Path('test/data/test.x'), Path('test/data/test.y')]
    
def test_path_expansion_dir_recursive():
    root_path = Path('test/data/')
    r = expand_path(root_path, "*.x", recursive=True)
    assert r == [Path('test/data/test.x'), Path('test/data/inner1/test2.x'), Path('test/data/inner1/inner2/test3.x')]
    r = expand_path(root_path, "*.y", recursive=True)
    assert r == [Path('test/data/test.y'), Path('test/data/inner1/test2.y'), Path('test/data/inner1/inner2/test3.y')]

def test_path_expansion_multiglob():
    root_path = Path('test/data/')
    r = expand_path(root_path, ['*.x', '*.y'], recursive=False)
    assert r == [Path('test/data/test.x'), Path('test/data/test.y')]
    r = expand_path(root_path, ['*.x', '*.y'], recursive=True)
    expected = [Path('test/data/test.x'), Path('test/data/test.y'),
                 Path('test/data/inner1/test2.y'), Path('test/data/inner1/test2.x'),
                 Path('test/data/inner1/inner2/test3.x'), Path('test/data/inner1/inner2/test3.y')]
    diff = set(r) ^ set(expected)
    assert not diff


