from typing import List, Generator, Tuple
from pathlib import Path
from json import loads, JSONDecodeError
import logging

from referencing import Registry
from referencing.exceptions import Unresolvable
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from .schema import Schema
from .types import BuildError, ErrorSeverity

class MissingKeyException (Exception):
    pass

class JSONSchemaResource:
    path : Path
    raw : str
    json : dict
    id : str
    spec : str

    def __init__(self, path, build_errors : List[BuildError]):
        self.path = path
        self.raw = path.read_text()
        self.json = loads(self.raw)
        if "$id" in self.json.keys():
            self.id = self.json['$id']
        else:
            raise MissingKeyException("Schema has no $id key")
        if '$schema' in self.json.keys():
            self.spec = self.json['$schema']
        else:
            build_errors.append(BuildError(path, ErrorSeverity.WARNING, MissingKeyException(f"Schema {self.id} has no specification ('$schema') key")))
            self.spec = "https://json-schema.org/draft/2020-12/schema"
            self.json['$schema'] = "https://json-schema.org/draft/2020-12/schema"

class JSONSchema(Schema):
    def __init__(self, core_schema : Path, supporting_schemas : List[Path], expand_errors : bool = True):
        super().__init__(core_schema, supporting_schemas, ["schema.json"])
        self.expand_errors = expand_errors

    def build(self) -> bool:
        self.build_errors.clear()
        self.built_ok = False

        try:
            self.core_schema = JSONSchemaResource(self.core_schema_path, self.build_errors)
        except Exception as ex:
            self.build_errors.append(BuildError(self.core_schema_path, ErrorSeverity.ERROR, ex))
            self.core_schema = None

        self.supporting_schemas = []
        for path in self.supporting_schemas_paths:
            try:
                self.supporting_schemas.append(JSONSchemaResource(path, self.build_errors))
            except Exception as ex:
                self.build_errors.append(BuildError(path, ErrorSeverity.ERROR, ex))
        
        if self.core_schema is None:
            return False
        
        try:
            self.registry = Registry().with_contents([(r.id, r.json) for r in self.supporting_schemas] + [(self.core_schema.id, self.core_schema.json)])
            self.validator = Draft202012Validator(self.core_schema.json, registry=self.registry)
            Draft202012Validator.check_schema(self.core_schema.json)
        except Exception as ex:
            self.build_errors.append(BuildError(None, ErrorSeverity.ERROR, ex))
            return False
        
        ref_errors = self._check_all_refs()
        if len(ref_errors) > 0:
            self.build_errors += ref_errors
            return False
        
        self.built_ok = True
        return True

    def _check_all_refs(self) -> List[Exception]:
        errors = self._check_refs(self.core_schema)
        for other_schema in self.supporting_schemas:
            errors += self._check_refs(other_schema)
        return errors
    
    def _check_refs(self, schema) -> List[Exception]:
        refs = list(self._recursively_find_refs(schema.json))
        resource = self.registry.get(schema.id)
        resolver = self.registry.resolver_with_root(resource)
        errors = []
        for key, ref in refs:
            try:
                resolver.lookup(ref)
            except Unresolvable as ex:
                errors.append(BuildError(schema.path, ErrorSeverity.ERROR, ex))
        return errors
    
    def _recursively_find_refs(self, j) -> Generator[Tuple[str, str], None, None]:
        if isinstance(j, dict):            
            for k,v in j.items():
                if k == "$ref":
                    yield k,v
                else:
                    yield from self._recursively_find_refs(v)
        elif isinstance(j, list):
            for i in j:
                yield from self._recursively_find_refs(i)
        else:
            return

    def validate_string(self, string: str) -> List[Exception]:
        errors = []
        try:
            instance_json = loads(string)
        except JSONDecodeError as ex:
            return [ex]        
        for error in self.validator.iter_errors(instance_json):
            errors += self.expandError(error)
        return errors

    def validate(self, instance_doc: Path) -> List[Exception]:
        try:
            return self.validate_string(instance_doc.read_text())
        except (PermissionError, FileNotFoundError) as ex:
            return [ex]

    def expandError(self, ex : Exception):
        if not self.expand_errors:
            return ex
        if not isinstance(ex, ValidationError):
            logging.debug("Not a Validation Error " + str(type(ex)))
            return ex
        if ex.schema_path[-1] == "oneOf":
            logging.debug(ex.absolute_path)
            logging.debug("Looks like a oneOf problem")
            logging.debug("Valid options are...")
            for thing in ex.schema['oneOf']:
                logging.debug ("Maybe " + str(thing))
                if "$ref" in thing:
                    resolved = self.registry.resolver().lookup(thing['$ref'])
                    candidate_def = resolved.contents
                else:
                    candidate_def = thing

                if ("required" in candidate_def
                    and len(candidate_def["required"]) > 0
                    and candidate_def["required"][0] in ex.instance
                    ):
                    candidate_field = candidate_def["required"][0]
                    candidate_ref = candidate_def["properties"][candidate_field]
                    if (candidate_field == '@xsi:type'
                        and 'properties' in candidate_def
                        and '@xsi:type' in candidate_def['properties']):
                        expected_type = candidate_def['properties']['@xsi:type']['enum'][0]
                        if '@xsi:type' in ex.instance:
                            if ex.instance['@xsi:type'] == expected_type:
                                candidate_ref = thing
                                test_instance = ex.instance
                            else:
                                logging.debug("xsi type doesn't match, moving on")
                                continue
                        else:
                            logging.debug ("No xsi type in instance, moving on")
                            continue
                    else:
                        logging.debug("Doesn't look like xsi:type, trying ref directly")
                        #TODO need to determine correct source document in order for this to 
                        # work e.g. in TrafficPolicy
                        likely_ns = self.validator.schema["$id"]
                        if candidate_field.startswith("tp:"):
                            likely_ns = 'ts_103120_TrafficPolicy_2022_07'
                            # quick hack
                            # TODO remove this
                        candidate_ref['$ref'] = likely_ns + candidate_ref['$ref']
                        try:
                            resolved = self.registry.resolver().lookup(candidate_ref['$ref'])
                        except Exception as inner_ex:
                            logging.debug(f"Failed resolving {candidate_ref} ({inner_ex}), carrying on")
                            continue
                        if not resolved:
                            logging.debug(f"Could resolve {candidate_ref}, carrying on")
                            continue
                        test_instance = ex.instance[candidate_field]
                else:
                    logging.debug("Doesn't look like it matches this oneOf option, moving on")
                    continue
                
                logging.debug ("Having a go at matching:")
                logging.debug(candidate_ref)
                logging.debug(test_instance)
                fragment_validator = Draft202012Validator(candidate_ref, registry=self.registry)
                new_errors = list(fragment_validator.iter_errors(test_instance))
                for error in new_errors:
                    expanded_errors = self.expandError(error)
                    if len(expanded_errors) == 0:
                        return ex
                    else:
                        for expanded_error in expanded_errors:
                            expanded_error.path = ex.path + error.path
                        return expanded_errors
            logging.debug("No valid options, returning self")
            return [ex]
        else:
            logging.debug("Some other kind of error")
            return [ex]