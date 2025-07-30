
from abc import ABC
from typing import List
from pathlib import Path

from .helpers import expand_path
from .types import BuildError

class Schema(ABC):
    def __init__ (self, core_schema : Path, supporting_schemas : List[Path], extensions : List[str]):
        self.core_schema_path = core_schema
        self.supporting_schemas_paths = [expanded_path for path in supporting_schemas for expanded_path in expand_path(path, [f'*.{x}' for x in extensions])]
        self.build_errors : List[BuildError] = []
        self.core_schema = None
        self.supporting_schemas = []
        self.built_ok = False
    
    def build(self) -> bool:
        pass

    def validate_string(self, string: str) -> List[Exception]:
        pass

    def validate(self, instance_doc: Path) -> List[Exception]:
        pass

