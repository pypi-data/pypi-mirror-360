
from typing import List
from pathlib import Path

from json import loads, JSONDecodeError
from xml.etree.ElementTree import parse, ParseError

import logging

def expand_path(path: Path, globs:List[str] | str, recursive: bool = True, case_sensitive = False):
    if not path.exists():
        return [path]
    if not path.is_dir():
        return [path]
    if recursive:
        if isinstance(globs, str):
            return [f for f in path.rglob(globs, case_sensitive=case_sensitive)]
        else:
            return [f for glob in globs for f in path.rglob(glob, case_sensitive=case_sensitive)]
    else:
        if isinstance(globs, str):
            return [f for f in path.glob(globs, case_sensitive=case_sensitive)]
        else:
            return [f for glob in globs for f in path.glob(glob, case_sensitive=case_sensitive)]

def guess_encoding (file: Path):
    logging.debug(f"Attempting to guess encoding of {file}")
    if file.suffix.lower() == ".json":
        logging.debug(f"Guessing json from extension")
        return "json"
    if file.suffix.lower() in [".xml", ".xsd"]:
        logging.debug(f"Guessing XML from extension")
        return "xml"

    if not file.exists():
        logging.warning(f"Couldn't open {file} to check contents for encoding")
        return None
    
    try:
        j = loads(file.read_text())
        logging.info(f"JSON encoding detected contents of {file}")
        return "json"
    except JSONDecodeError as ex:
        logging.debug("Decoding contents as JSON failed")

    try:
        et = parse(str(file))
        logging.info(f"XML encoding detected from contents of {file}")
        return "xml"
    except ParseError as ex:
        logging.debug("Decoding contents as XML failed")

    return None