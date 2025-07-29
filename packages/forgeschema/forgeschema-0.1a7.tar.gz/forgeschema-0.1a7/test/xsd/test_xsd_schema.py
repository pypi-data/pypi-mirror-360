from pathlib import Path
from typing import List

from xmlschema import XMLSchemaValidationError, XMLSchemaParseError
from urllib.error import URLError
from xml.etree.ElementTree import ParseError
from pytest import mark

from forgeschema import XSDSchema
from forgeschema.types import ErrorSeverity



def test_xsd():
    s = XSDSchema(Path('test/xsd/set1/good.xsd'), [])
    s.build()
    assert s.built_ok

@mark.parametrize("instance_path, expected_exception", [
    (Path('test/xsd/set1/bad_namespace.xml'), XMLSchemaValidationError),
    (Path('test/xsd/set1/bad_not_compliant.xml'), XMLSchemaValidationError),
    (Path('test/xsd/set1/bad_syntax.xml'), ParseError),
])
def test_simple_fails_validation(instance_path: Path, expected_exception):
    s = XSDSchema(Path('test/xsd/set1/good.xsd'), [])
    s.build()
    errors = s.validate(instance_path)
    assert len(errors) == 1
    assert isinstance(errors[0], expected_exception)


@mark.parametrize("core_schema, expected_exception", [
    (Path('thisfiledoesntexist'), URLError),
    (Path('test/xsd/set1/bad_syntax.xml'), ParseError)
])
def test_bad(core_schema: Path, expected_exception):
    s = XSDSchema(core_schema, [])
    s.build()
    assert not s.built_ok
    assert len(s.build_errors) == 1
    b = s.build_errors[0]
    assert isinstance(b.error, expected_exception) 


def test_bad_supporting():
    s = XSDSchema(Path('thisfiledoesntexist'), [Path('nordoesthisone.xsd')])
    s.build()
    assert not s.built_ok
    assert len(s.build_errors) == 2
    assert isinstance(s.build_errors[0].error, URLError) 
    assert isinstance(s.build_errors[1].error, URLError) 


@mark.parametrize("core_schema, supporting_schemas, instance_files",[
    (Path('test/xsd/set1/good.xsd'),[],[Path('test/xsd/set1/good.xml')]),
    (Path('test/xsd/set2/good_with_import.xsd'),
         [Path('test/xsd/set2/good_imported.xsd')],
         [Path('test/xsd/set2/good.xml')])
])
def test_matches_xsd(core_schema : Path, supporting_schemas : List[Path], instance_files : List[Path]):
    s = XSDSchema(core_schema, supporting_schemas)
    s.build()
    assert s.built_ok
    for instance in instance_files:
        errors = s.validate(instance)
        assert len(errors) == 0

@mark.parametrize("core_schema, expected_error",[
    (Path('test/xsd/bad_xsds/missing_element_name.xsd'),XMLSchemaParseError),
    (Path('test/xsd/bad_xsds/complex_content.xsd'),XMLSchemaParseError)
])
def test_bad_xsds(core_schema : Path, expected_error):
    s = XSDSchema(Path(core_schema), [])
    s.build()
    assert not s.built_ok
    assert len(s.build_errors) == 1
    assert isinstance(s.build_errors[0].error, expected_error)