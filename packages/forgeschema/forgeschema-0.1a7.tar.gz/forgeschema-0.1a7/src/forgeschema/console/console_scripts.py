import logging
import json
from sys import stdin
from argparse import ArgumentParser
from pathlib import Path
from xml.etree import ElementTree

from rich.table import Table
from rich import box
from rich.console import Console

from ..schema import Schema
from ..jsonschema import JSONSchema
from ..xsdschema import XSDSchema
from ..types import ErrorSeverity
from ..helpers import guess_encoding, expand_path
from ..render import render_validation_output


ERR_FILE_NOT_FOUND          = -1
ERR_UNSUPPORTED_ENCODING    = -2
ERR_UNKNOWN_ENCODING        = -3
ERR_BAD_CONFIG              = -4

EXIT_OK                     = 0
EXIT_BUILD_ERRORS           = 1
EXIT_VALIDATION_ERRORS      = 2

supported_encodings = {
    'json' : {
        'schema_extensions' : ['.schema.json'],
        'instance_extensions' : ['.json']
    },
    'xml' : {
        'schema_extensions' : ['.xsd'],
        'instance_extensions' : ['.xml']
    }
}

def check():
    parser = ArgumentParser()

    parser = ArgumentParser(description="Build a schema set and use it to validate zero or more instance documents. Returns 1 if the schema build fails, 2 if any of the instance documents fail to validate, or 0 otherwise. If JSON output is selected via the -j switch, it is always 0")
    parser.add_argument("-e", "--encoding", help=f"Set the encoding of the schema / instance documents. One of [{'|'.join(list(supported_encodings.keys()))}]")
    arg_group = parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument("-c", "--config", help="Specifies the location of a JSON config file")
    arg_group.add_argument("-s", "--coreschema", help="Specifies the location of the core JSON schema file")
    parser.add_argument("-u", "--supportingschema", action="append", help="Specifies the location of any supporting schemas required. If a directory is specified, testjson will search and add any .schema.json files recursively within the directory")
    parser.add_argument("-i", "--instancedoc", action="append", help="Instance XML document to validate against the schema. If a directory is specified, xmltest will search and add any XML files recursively within the directory")
    parser.add_argument("-j", "--jsonoutput", action="store_true", help="Output JSON instead of text. Return code will always be zero")
    parser.add_argument("-v", "--verbose", action="count", help="Verbose. Can be specified multiple times to get more detailed output")
    parser.add_argument("--showbuild", action="store_true", help="Print build output to stdout")
    parser.add_argument("--showvalidation", action="store_true", help="Print validation output to stdout")
    parser.add_argument("--hideissues", action="store_true", help="Print list of build and validation issues to stdout")
    parser.add_argument("--hidesummary", action="store_true", help="Hide summary output on stdout")
    parser.add_argument("-q", "--quiet", action="store_true", help="Hide all output (equivalent to --hideissues plus --hidesummary)")
    pargs = parser.parse_args()

    if pargs.verbose is None or pargs.verbose == 1:
        logging.basicConfig(level=logging.ERROR)
    elif pargs.verbose == 2:
        logging.basicConfig(level=logging.WARNING)
    elif pargs.verbose == 3:
        logging.basicConfig(level=logging.INFO)
    elif pargs.verbose > 3:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)
    
    logging.debug(f"Called with arguments {pargs}")

    if pargs.config is not None:
        config_file = Path(pargs.config)
        if not config_file.exists():
            logging.error(f"Cannot find config file {pargs.config}")
            exit(ERR_FILE_NOT_FOUND)
        config = json.loads(config_file.read_text())
        if 'coreSchema' not in config.keys():
            logging.error('Config file does not have a "coreSchema" key')
            exit(ERR_BAD_CONFIG)
        if 'supportingSchemas' not in config.keys():
            logging.warning('Config file does not have a "supportingSchemas" key, assuming empty')
            config['supportingSchemas'] = []
        if 'instanceDocs' not in config.keys():
            logging.warning('Config file does not have a "instanceDocs" key, assuming empty')
            config['instanceDocs'] = []
    else:
        config = {
            'coreSchema' : pargs.coreschema,
            'supportingSchemas' : [s for s in pargs.supportingschema] if pargs.supportingschema is not None else [],
            'instanceDocs' : [i for i in pargs.instancedoc] if pargs.instancedoc is not None else [],
        }

    if pargs.encoding is None:
        if not (Path(config['coreSchema']).exists()):
            logging.error(f"Could not load core schema {config['coreSchema']}")
            exit(ERR_FILE_NOT_FOUND)
        logging.debug("No encoding specified, attempting to guess encoding from core schema...")
        guessed_encoding = guess_encoding(Path(config['coreSchema']))
        if guessed_encoding is None:
            logging.error(f"Couldn't guess encoding from {config['coreSchema']}")
            exit(ERR_UNKNOWN_ENCODING)
        else:
            pargs.encoding = guessed_encoding

    if pargs.encoding not in list(supported_encodings.keys()):
        logging.error(f"Unsupported encoding '{pargs.encoding}' specified. Supported encodings are [{'|'.join(list(supported_encodings.keys()))}]")
        exit(ERR_UNSUPPORTED_ENCODING)
    if pargs.encoding == 'xml':
        logging.debug("Creating XML schema")
        schema = XSDSchema(Path(config['coreSchema']), [Path(x) for x in config['supportingSchemas']])
    if pargs.encoding == 'json':
        logging.debug("Creating JSON schema")
        schema = JSONSchema(Path(config['coreSchema']), [Path(x) for x in config['supportingSchemas']])


    logging.debug("Expanding supporting schemas...")
    config['supportingSchemas'] = [expanded_path for path in config['supportingSchemas'] for expanded_path in expand_path(Path(path), [f'*{x}' for x in supported_encodings[pargs.encoding]['schema_extensions']])]
    if Path(config['coreSchema']) in config['supportingSchemas']:
        config['supportingSchemas'].remove(Path(config['coreSchema']))

    logging.debug("Expanding instance docs...")
    config['instanceDocs'] = [expanded_path for path in config['instanceDocs'] for expanded_path in expand_path(Path(path), [f'*{x}' for x in supported_encodings[pargs.encoding]['instance_extensions']])]

    logging.debug(f"Config: {config}")

    schema.build()

    if schema.built_ok:
        logging.info('Schema built OK')
        if len(config['instanceDocs']) == 1 and str(config['instanceDocs'][0]).lower() == 'stdin':
            input_string = stdin.read()
            validation_errors = {'stdin' : schema.validate_string(input_string)}
        else:
            validation_errors = {f : schema.validate(Path(f)) for f in config['instanceDocs']}
    else:
        logging.warning('Errors building schema')
        validation_errors = {}

    if pargs.jsonoutput:
        logging.debug("Giving output in JSON format")
        output = {
            'input' : config,
            'build_errors' : [be.toJSON() for be in schema.build_errors],
            'validation_errors' : validation_errors
        }
        print(json.dumps(output, default=str))
        exit(EXIT_OK)

    render_validation_output(schema, validation_errors, config, pargs.quiet, pargs.hidesummary, pargs.hideissues, pargs.showbuild, pargs.showvalidation)

    # fatal_build_errors = len([x for x in schema.build_errors if x.severity == ErrorSeverity.ERROR])
    # non_fatal_build_errors = len(schema.build_errors) - fatal_build_errors
    total_validation_errors = sum(len(v) for k,v in validation_errors.items())
        
    # console = Console()

    # if pargs.quiet:
    #     pargs.hidesummary = True
    #     pargs.hideissues = True
        
    # if pargs.showbuild:
    #     table = Table(show_header=True, expand=True, box=box.ROUNDED)
    #     table.add_column("Build input", justify="left")
    #     table.add_column("Status", justify="left", width=10)
    #     for input in [config['coreSchema']] + config['supportingSchemas']:
    #         errors_for_input = len([b for b in schema.build_errors if b.path == Path(input)])
    #         table.add_row(f"[bright_blue]{input}[/]", "[green]OK[/]" if errors_for_input == 0 else f"[bright_red]{errors_for_input} ERRORS[/]")
    #     console.print(table)
    # else:
    #     logging.debug("Hiding build output (use --showbuild to show)")

    # if pargs.showvalidation:
    #     if fatal_build_errors > 0:
    #         table = Table(show_header=False, expand=True, box=box.ROUNDED)
    #         table.add_row("[bright_red]No validation performed due to build failures[/]")
    #     else:
    #         table = Table(show_header=True, expand=True, box=box.ROUNDED)
    #         table.add_column("Validation input", justify="left")
    #         table.add_column("Status", justify="left", width=10)
    #         for input in config['instanceDocs']:                
    #             errors_for_input = len(validation_errors[input])
    #             table.add_row(f"[bright_blue]{input}[/]", "[green]OK[/]" if errors_for_input == 0 else f"[bright_red]{errors_for_input} ERRORS[/]")
    #     console.print(table)
    # else:
    #     logging.debug("Hiding validation output (use --showvalidation to show)")

    # if pargs.hideissues:
    #     logging.debug("Hiding issues list (omit --hideissues to show)")
    # else:
    #     if len(schema.build_errors) > 0:
    #         table = Table(show_header=True, expand=True, box=box.ROUNDED)
    #         table.add_column("Schema", width=8, justify="left")
    #         table.add_column("Issue", justify="left")
    #         table.add_column("Severity", justify="left")
    #         for build_error in schema.build_errors:
    #             table.add_row(f"[bright_blue]{build_error.path}[/]", f"[yellow]{build_error.error}[/]", f"[bright_red]ERROR[/]" if build_error.severity == ErrorSeverity.ERROR else "[yellow]WARNING[/]")
    #         console.print(table)
            
    #     if total_validation_errors > 0:
    #         table = Table(show_header=True, expand=True, box=box.ROUNDED)
    #         table.add_column("Document", width=8, justify="left")
    #         table.add_column("Issue", justify="left")
    #         for path, error_list in validation_errors.items():
    #             for error in error_list:
    #                 table.add_row(f"[bright_blue]{path}", f"[yellow]{error}[/]")
    #                 table.add_section()
    #         console.print(table)

    # if pargs.hidesummary:
    #     logging.debug("Hiding stats (omit --hidesummary to show)")
    # else:
    #     table = Table(show_header=False, expand=True, box=box.ROUNDED)
    #     table.add_column("Field", width=8, justify="left")
    #     table.add_column("Value", justify="left")
    #     table.add_row("Schemas", f"[bright_blue]{config['coreSchema']}[/] plus [bright_blue]{len(config['supportingSchemas'])}[/] supporting schemas")
    #     table.add_row("Build errors", f"{"[green]" if len(schema.build_errors) == 0 else "[bright_red]"}{fatal_build_errors}[/] fatal, {"[green]" if non_fatal_build_errors == 0 else "[yellow]"}{non_fatal_build_errors}[/] non-fatal")
    #     table.add_section()
    #     table.add_row("Instance docs validated", f"[bright_blue]{len(config['instanceDocs'])}[/]")
    #     if (len(config['instanceDocs'])) > 0:
    #         table.add_row("Validation failures", f"{"[green]" if total_validation_errors == 0 else "[bright_red]"}{total_validation_errors}[/]")
    #     table.add_section()
    #     if fatal_build_errors > 0:
    #         table.add_row("Outcome", "[bright_red]FAILED BUILD[/]")
    #     elif total_validation_errors > 0:
    #         table.add_row("Outcome", "[bright_red]FAILED VALIDATION[/]")
    #     else:
    #         table.add_row("Outcome", "[green]OK[/]")
    #     console.print(table)

    if not schema.built_ok:
        logging.warning(f"Schema had {len(schema.build_errors) } build errors. Exiting with code {EXIT_BUILD_ERRORS}")
        exit(EXIT_BUILD_ERRORS)
    if total_validation_errors > 0:
        logging.warning(f"Schema built OK but there were {total_validation_errors} validation errors in instance documents. Exiting with code {EXIT_VALIDATION_ERRORS}")
        exit(EXIT_VALIDATION_ERRORS)

    exit(EXIT_OK)