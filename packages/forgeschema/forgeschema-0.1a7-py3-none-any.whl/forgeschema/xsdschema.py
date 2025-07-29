from typing import List, Generator, Tuple
from pathlib import Path

from xmlschema import XMLSchema
from xmlschema.exceptions import XMLSchemaException
from xml.etree.ElementTree import ParseError

from .schema import Schema
from .types import BuildError, ErrorSeverity

class XSDSchemaResource:
    path : Path
    schema : XMLSchema
    namespace : str
    
    def __init__(self, path, build_errors: List[BuildError]):
        self.path = path
        self.schema = XMLSchema(str(path), validation='skip')
        self.namespace = self.schema.target_namespace
        # For some reason we get spurious UPA errors in the supporting schemas
        # so these are filtered out. A real UPA error will be caught when the
        # schema set if built with "strict" later on.
        build_errors += [
            BuildError(path, ErrorSeverity.ERROR, error)
            for error in self.schema.all_errors
            if not error.message.startswith("Unique Particle Attribution violation")
        ]


class XSDSchema(Schema):
    def __init__(self, core_schema : Path, supporting_schemas : List[Path]):
        super().__init__(core_schema, supporting_schemas, ["xsd"])
    
    def build(self) -> bool:
        self.build_errors.clear()
        self.built_ok = False

        self.supporting_schemas = []
        for schema_path in self.supporting_schemas_paths:
            try:
                self.supporting_schemas.append(XSDSchemaResource(schema_path, self.build_errors))
            except Exception as ex:
                self.build_errors.append(BuildError(schema_path, ErrorSeverity.ERROR, ex))
        
        schema_locations = [(r.namespace, str(r.path.resolve())) for r in self.supporting_schemas]

        try:
            self.core_schema = XMLSchema(str(self.core_schema_path), locations = schema_locations, validation='strict')
        except Exception as ex:
            self.build_errors.append(BuildError(self.core_schema_path, ErrorSeverity.ERROR, ex))
            return False

        self.built_ok = True
        return True

    def validate_string(self, string:str) -> List[Exception]:
        try:
            return list(self.core_schema.iter_errors(string))
        except (ParseError, XMLSchemaException) as ex:
            return [ex]

    def validate(self, instance_doc: Path) -> List[Exception]:
        if not instance_doc.exists():
            return [FileNotFoundError(instance_doc)]
        try:
            errors = list(self.core_schema.iter_errors(str(instance_doc)))
        except Exception as ex:
            errors = [ex]
        return errors