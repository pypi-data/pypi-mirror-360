import logging
from pathlib import Path

from rich.table import Table
from rich import box
from rich.console import Console

from .schema import Schema
from .types import BuildError, ErrorSeverity

import colorama
from colorama import  Fore, Style

colorama.init()
RED = Fore.RED
GRN = Fore.GREEN
BLU = Fore.BLUE
YLW = Fore.YELLOW
CLR = Style.RESET_ALL

def render_single_validation(schema: Schema, validation_errors):
    console = Console()
    table = Table(show_header=True, expand=True, box=box.ROUNDED)
    table.add_column("Issue", justify="left")
    for error in validation_errors:
        table.add_row(f"[yellow]{error}[/]")
        table.add_section()
    console.print(table)

def render_validation_output(schema: Schema, validation_errors, config, quiet = False, hide_summary = False, hide_issues = False, show_build = False, show_validation = False, hide_build_summary = False):
    fatal_build_errors = len([x for x in schema.build_errors if x.severity == ErrorSeverity.ERROR])
    non_fatal_build_errors = len(schema.build_errors) - fatal_build_errors
    total_validation_errors = sum(len(v) for k,v in validation_errors.items())
        
    console = Console()

    if quiet:
       hide_summary = True
       hide_issues = True
        
    if show_build:
        table = Table(show_header=True, expand=True, box=box.ROUNDED)
        table.add_column("Build input", justify="left")
        table.add_column("Status", justify="left", width=10)
        for input in [config['coreSchema']] + config['supportingSchemas']:
            errors_for_input = len([b for b in schema.build_errors if b.path == Path(input)])
            table.add_row(f"[bright_blue]{input}[/]", "[green]OK[/]" if errors_for_input == 0 else f"[bright_red]{errors_for_input} ERRORS[/]")
        console.print(table)
    else:
        logging.debug("Hiding build output (use --showbuild to show)")

    if show_validation:
        if fatal_build_errors > 0:
            table = Table(show_header=False, expand=True, box=box.ROUNDED)
            table.add_row("[bright_red]No validation performed due to build failures[/]")
        else:
            table = Table(show_header=True, expand=True, box=box.ROUNDED)
            table.add_column("Validation input", justify="left")
            table.add_column("Status", justify="left", width=10)
            for input in config['instanceDocs']:                
                errors_for_input = len(validation_errors[input])
                table.add_row(f"[bright_blue]{input}[/]", "[green]OK[/]" if errors_for_input == 0 else f"[bright_red]{errors_for_input} ERRORS[/]")
        console.print(table)
    else:
        logging.debug("Hiding validation output (use --showvalidation to show)")

    if hide_issues:
        logging.debug("Hiding issues list (omit --hideissues to show)")
    else:
        if len(schema.build_errors) > 0:
            table = Table(show_header=True, expand=True, box=box.ROUNDED)
            table.add_column("Schema", justify="left")
            table.add_column("Issue", justify="left", no_wrap=False)
            table.add_column("Severity", justify="left")
            for build_error in schema.build_errors:
                table.add_row(f"[bright_blue]{build_error.path.name}[/]", f"[yellow]{repr(build_error.error)}[/]", f"[bright_red]ERROR[/]" if build_error.severity == ErrorSeverity.ERROR else "[yellow]WARNING[/]")
            console.print(table)
            
        if total_validation_errors > 0:
            for path, error_list in validation_errors.items():
                if len(error_list) == 0:
                    continue
                table = Table(show_header=False, expand=True, box=box.ROUNDED)
                table.add_row(f"[bright_blue]{path}:[/] [bright_red]{len(error_list)}[/] issues")
                for error in error_list:
                    table.add_section()
                    table.add_row(f"[yellow]{error}[/]")
                console.print(table)

    if hide_summary:
        logging.debug("Hiding summary (omit --hidesummary to show)")
    else:
        print ("────────────────────────────────────────────────────────────────────────────")
        print (f"Building {BLU}{config['coreSchema']}{CLR} and {BLU}{len(config['supportingSchemas'])}{CLR} supporting schemas")
        if fatal_build_errors > 0:
            print (f"❌ Failed build, {RED}{fatal_build_errors}{CLR} fatal, {non_fatal_build_errors} non-fatal")

            for build_error in schema.build_errors:
                print ("────────────────────────────────────────────────────────────────────────────")
                print (f"Build error in {BLU}{build_error.path}{BLU}")
                print (f"")
                print (f"{YLW}{build_error.error}{CLR}")
                
        else:
            print (f"✅ Built OK")
            if total_validation_errors > 0:
                print (f"❌ Failed validating instance documents")
            else:
                print (f"✅ Validated {BLU}{len(config['instanceDocs'])}{CLR} instance documents")
        print ("────────────────────────────────────────────────────────────────────────────")