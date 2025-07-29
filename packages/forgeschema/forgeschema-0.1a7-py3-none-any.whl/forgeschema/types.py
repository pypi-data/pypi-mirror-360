from dataclasses import dataclass
from pathlib import Path
from typing import List
from enum import IntEnum

from json import JSONDecodeError



@dataclass
class SchemaBuildSet:
    core_schema : Path
    supporting_schemas : List[Path]
    
class ErrorSeverity(IntEnum):
    INFO = 1
    WARNING = 2
    ERROR = 3

@dataclass 
class BuildError:
    path: Path
    severity : ErrorSeverity
    error: Exception = None

    def toJSON(self):
        return {
            'path' : str(self.path.resolve()),
            'severity' : int(self.severity),
            'error' : repr(self.error)
        }