from pathlib import Path
from typing import List
from json import JSONDecodeError

from referencing.exceptions import Unresolvable
from jsonschema import ValidationError
from pytest import mark

from forgeschema.jsonschema import JSONSchema, MissingKeyException
from forgeschema.types import ErrorSeverity


@mark.parametrize("input_file, expected_exception", [
    (Path('not_a_file'), FileNotFoundError),
    (Path('test/json/bad_data/empty.schema.json'), JSONDecodeError),
    (Path('test/json/bad_data/invalid.schema.json'), JSONDecodeError),
    (Path('test/json/bad_data/noid.schema.json'), MissingKeyException),
    (Path('test/json/bad_data/invalid_ref.schema.json'), Unresolvable),
    (Path('test/json/bad_data/unresolvable_ref.schema.json'), Unresolvable),
    (Path('test/json/bad_data/unresolvable_2.schema.json'), Unresolvable),
    (Path('test/json/bad_data/unresolvable_3.schema.json'), Unresolvable),
])
def test_single_error(input_file: Path, expected_exception):
    s = JSONSchema(input_file, [])
    s.build()
    assert s.built_ok == False
    assert len(s.build_errors) == 1
    b = s.build_errors[0]
    assert b.path == input_file
    assert b.severity == ErrorSeverity.ERROR
    assert isinstance(b.error, expected_exception)


@mark.parametrize("core_schema, supporting_schemas", [
    (Path('test/json/simple/simple.schema.json'), []),
    (Path('test/json/ref/imports.schema.json'), [Path('test/json/ref/imported.schema.json')]),
])
def test_builds_with_no_errors(core_schema: Path, supporting_schemas : List[Path]):
    s = JSONSchema(core_schema, supporting_schemas)
    s.build()
    assert s.built_ok
    assert len(s.build_errors) == 0


def test_simple_without_spec():
    s = JSONSchema(Path('test/json/simple/simple_without_spec.schema.json'), [])
    s.build()
    assert len(s.build_errors) == 1
    b = s.build_errors[0]
    assert b.severity == ErrorSeverity.WARNING
    assert isinstance(b.error, Exception)
    assert s.built_ok


def test_validate_valid():
    s = JSONSchema(Path('test/json/simple/simple.schema.json'), [])
    s.build()
    assert s.built_ok
    errors = s.validate(Path('test/json/simple/instances/simple.json'))
    assert len(errors) == 0


def test_validate_invalid():
    s = JSONSchema(Path('test/json/simple/simple.schema.json'), [])
    s.build()
    assert s.built_ok
    errors = s.validate(Path('test/json/simple/instances/invalid.json'))
    assert len(errors) == 1
    assert isinstance(errors[0], ValidationError)

def test_indirect_ref_failure():
    s = JSONSchema(Path('test/json/bad_data/unresolvable_indirect.schema.json'), 
                   [Path('test/json/bad_data/unresolvable_3.schema.json')])
    s.build()
    assert not s.built_ok
    assert len(s.build_errors) == 1
    assert isinstance(s.build_errors[0].error, Unresolvable)
