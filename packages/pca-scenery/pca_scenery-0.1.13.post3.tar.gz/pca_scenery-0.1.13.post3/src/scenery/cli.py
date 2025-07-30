import argparse
import collections
import logging
import statistics
import unittest
from typing import Any, Callable, Iterable, Tuple

from scenery import logger, console
from scenery.common import serialize_unittest_result

from rich import box
from rich.console import Console
from rich.rule import Rule
from rich.progress import Progress, BarColumn, TextColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel



##################
# COMMAND WRAPPER
##################


def command(func: Callable) -> Callable:
    def wrapper(*args: Any) -> Any:

        command_label = func.__name__.replace("_", " ").capitalize()

        console.print(Rule(f"[section]{command_label} start...[/section]", style="cyan"))
        # logger.info(f"starting {func.__name__}...")

        success = func(*args)

        emojy, msg, color, log_lvl = interpret(success)
        console.print(Rule(f"{emojy} {command_label} {msg}", style=color))

        return success

    return wrapper


#################
# PARSE ARGUMENTS
#################


def parse_args() -> argparse.Namespace:
    """Parse command line arguments with subcommands."""
    parser = argparse.ArgumentParser(description="Scenery Testing Framework")

    # Add subparsers
    subparsers = parser.add_subparsers(dest="command", help="Testing command to run")
    parse_integration_args(subparsers)
    parse_load_args(subparsers) 
    parse_inspect_args(subparsers) 

    args = parser.parse_args()

    if hasattr(args, "test"):
        args.manifest, args.case_id, args.scene_pos = parse_arg_test_restriction(args.test)

    logger.level = logging._nameToLevel[args.log]

    return args


def add_common_testing_arguments(parser: argparse.ArgumentParser) -> None:

    parser.add_argument(
        "--config",
        dest="config",
        type=str,
        default="scenery.ini",
        help="Location of scenery settings module",
    )

    parser.add_argument(
        "--env",
        dest="env",
        type=str,
        default=".env",
        help="Location of env variables (for test credentials)",
    )

    # parser.add_argument(
    #     "--port",
    #     dest="port",
    #     type=str,
    #     default="8020",
    #     help="Port on which the server runs",
    # )

    parser.add_argument(
        "--django-settings",
        dest="django_settings_module",
        type=str,
        default=None,
        help="Location of django settings module, if needed",
    )

    parser.add_argument(
        "--test",
        nargs="?",
        default=None,
        help="Optional test restriction <manifest>.<case>.<scene>",
    )

    parser.add_argument(
        "--url",
        nargs="?",
        default=None,
        help="Optional url restriction",
    )

    parser.add_argument(
        "--log",
        nargs="?",
        default="INFO",
        help="Log level",
    )


def parse_arg_test_restriction(test_name_pattern: str|None) -> Tuple[str|None, str|None, str|None]:
    """Parse the --test argument into a tuple of (manifest_name, case_id, scene_pos)."""
    if test_name_pattern is not None:
        split_pattern = test_name_pattern.split(".")
        if len(split_pattern) == 1:
            manifest_name, case_id, scene_pos = split_pattern[0], None, None
        elif len(split_pattern) == 2:
            manifest_name, case_id, scene_pos = split_pattern[0], split_pattern[1], None
        elif len(split_pattern) == 3:
            manifest_name, case_id, scene_pos = split_pattern[0], split_pattern[1], split_pattern[2]
        else:
            raise ValueError(f"Wrong restrict argmuent {test_name_pattern}")
        return manifest_name, case_id, scene_pos
    else:
        return None, None, None


def parse_integration_args(subparser: argparse._SubParsersAction) -> None:
    """Parse command line arguments."""

    parser = subparser.add_parser('integration', help='Integration tests')
    add_common_testing_arguments(parser)
    
    parser.add_argument('--back', action='store_true')
    parser.add_argument('--front', action='store_true')

    parser.add_argument(
        "--mode",
        choices=["dev", "local", "staging", "prod"],
        default="dev"
    )

    # parser.add_argument(
    #     "--timeout",
    #     dest="timeout_waiting_time",
    #     type=int,
    #     default=5,
    # )

    parser.add_argument(
        "--page-load-timeout",
        dest="page_load_timeout",
        type=int,
        default=5,
    )

    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--failfast', action='store_true')



def parse_load_args(subparser: argparse._SubParsersAction) -> None:

    parser = subparser.add_parser('load', help='Load tests')
    add_common_testing_arguments(parser)


    parser.add_argument(
        "--mode",
        choices=["local", "staging", "prod"],
    )

    parser.add_argument('-u', '--users', type=int)
    parser.add_argument('-r', '--requests', type=int)

def parse_inspect_args(subparser: argparse._SubParsersAction) -> None:

    parser = subparser.add_parser('inspect', help='Inspect files')

    parser.add_argument('-f', '--folder', type=str, help='Folder to inspect')

    parser.add_argument(
        "--log",
        nargs="?",
        default="INFO",
        help="Log level",
    )

#################
# RICH HELPERS
#################


def table_from_dict(d: dict[str, Any], col1_title : str = "", col2_title:str = "", title: str | None =None, formatting: dict[str, Tuple[str, Any]]={}) -> Table:
        
    show_header = col1_title != "" or col2_title != ""
    table = Table(title=title, box=box.ROUNDED, show_header=show_header)
    table.add_column(col1_title, style="cyan", no_wrap=True)
    table.add_column(col2_title, justify="right")

    for key, value in d.items():

        format_str, color = formatting.get(key, ("{}", None))
        label = str(key).replace("_", " ").capitalize()
        row_values = [label,]
        value = d.get(key)
        formatted_value = format_str.format(value)
        if color:
            formatted_value = f"[{color}]{formatted_value}[/{color}]"
        row_values.append(formatted_value)
        
        table.add_row(*row_values)
    
    return table

def histogram(x: Iterable[int]) -> Progress:
    """Display a histogram leveraging Rich progress bars and return a renderable object"""
    # Calculate histogram data
    max_val = max(x)
    
    bins = [
        (0, 50), 
        (50, 100), 
        (100, 200),
        (100, 300),
        (300, 500),
        (500, 750),
        (750, 1000),
        (1000, 2000),
        (2000, 3000),
        (3000, max(max_val, 4000))]

    histogram_data = []
    # for i in range(bins):
        # bin_start = min_val + i * bin_width
        # bin_end = min_val + (i + 1) * bin_width
    for i, (bin_start, bin_end) in enumerate(bins):
        bin_count = sum(1 for t in x if bin_start <= t < bin_end or (i == len(bins)-1 and t == bin_end))
        # bin_count = sum(1 for t in x if bin_start <= t < bin_end or (i == bins-1 and t == bin_end))
        histogram_data.append((bin_start, bin_end, bin_count))
    
    max_count = sum(count for _, _, count in histogram_data) if histogram_data else 0
    completed_style = Style(color="white")
    
    # Create a custom Progress object that can be rendered later
    progress = Progress(
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=50, complete_style=completed_style),
        TextColumn("{task.completed} requests"),
        expand=False,
    )
    
    # Add tasks to the progress object
    for bin_start, bin_end, count in histogram_data:
        desc = f"{bin_start:.0f}ms - {bin_end:.0f}ms"
        progress.add_task(desc, total=max_count, completed=count)
    
    # Return the progress object itself (which is renderable)
    return progress




##################
# REPORTS
##################


def summarize_test_result(result: unittest.TestResult, test_label: str) -> Tuple[bool, collections.Counter]:
    """Return true if the tests all succeeded, false otherwise."""
    for failed_test, traceback in result.failures:
        test_name = failed_test.id()
        emojy, msg, color, log_lvl = interpret(False)
        # logger.log(log_lvl, f"[{color}]{test_name} {msg}[/{color}]\n{traceback}")
        logger.log(log_lvl, f"{test_name} {msg}", style=color)
        # console.print_exception(
        #     exc_info=(None, None, traceback),
        #     show_locals=True
        # )
        # console.print(traceback)

    for failed_test, traceback in result.errors:
        test_name = failed_test.id()
        emojy, msg, color, log_lvl = interpret(False)
        # logger.log(log_lvl, f"[{color}]{test_name} {msg}[/{color}]\n{traceback}")
        logger.log(log_lvl, f"{test_name} {msg}", style=color)
        # console.print(traceback)

    success = True
    summary = serialize_unittest_result(result)
    if summary["errors during execution"] > 0 or summary["failed assertions"] > 0:
        success = False
    # if summary["testsRun"] == 0:
    #     pass

    else:
        emojy, msg, color, log_lvl = interpret(success)
        msg = f"{test_label} {msg}"
        logger.log(log_lvl, msg, style=color)

    return success, summary


def interpret(success: bool) -> Tuple[str, str, str, int]:
    """Return emojy, success/failure message, color and log level corresponding to the succes of an execution."""
    if success:
        emojy, msg, color, log_lvl = "🟢", "passed", "green", logging.INFO
    else:
        emojy, msg, color, log_lvl = "❌", "failed", "red", logging.ERROR
    return emojy, msg, color, log_lvl



def report_integration(data: dict) -> bool:


    panel_msg = ""
    panel_color = "green"
    report_tables = []

    command_level_success = True

    for key, val in data.items():

        key_level_success = True
        key_level_summary : dict[str, int] = collections.Counter()

        for success, summary in val:
            
            key_level_success &= success
            key_level_summary.update(summary)

        if val:
            emojy, msg, color, log_lvl = interpret(key_level_success)

            if key_level_success:
                msg = f"all {key} tests {msg}"
            else:
                msg = f"some {key} tests {msg}"
                panel_color = "red"

            logger.log(log_lvl, msg, style=color)
            if panel_msg != "":
                panel_msg += "\n"
            panel_msg += f"{emojy} {msg}"
            report_tables.append(table_from_dict(key_level_summary, key, ""))

            command_level_success &= key_level_success

    emojy, msg, color, log_lvl = interpret(command_level_success)
    logger.log(log_lvl, f"integration tests {msg}", style=color)

    fmt_tables = Columns(report_tables, equal=False, expand=True)
    panel_report = Group(panel_msg, fmt_tables)

    console.print(Panel(panel_report, title="Results", border_style=panel_color))


    return command_level_success



def report_load(data: dict, threshold_p95: int = 500, threshold_p99: int = 5000) -> bool:

    #####################
    # OUTPUT
    #####################

    command_level_success = True


    console = Console()

    for endpoint, requests_results in data.items():

        total_requests = len(requests_results)
        if total_requests == 0:
            continue

        successes = [r for r in requests_results if r["success"]]
        failures = [r for r in requests_results if not r["success"] ]

        success_times = [r['elapsed_time']*1000 for r in successes]
        error_times = [r['elapsed_time']*1000 for r in failures]
        
        error_rate = (len(error_times) / total_requests) * 100 if total_requests > 0 else 0
        
        ep_analysis = {
            'total_requests': total_requests,
            'successful_requests': len(success_times),
            'failed_requests': len(error_times),
            'error_rate': error_rate
        }


        
        if success_times:
            quantiles = statistics.quantiles(success_times, n=100)
            # quantiles = statistics.quantiles(success_times, n=4)

            p50 = statistics.median(success_times)
            p90 = quantiles[90-1]
            p95 = quantiles[95-1]
            p99 = quantiles[99-1]

            ep_analysis.update({
                'min_time': min(success_times),
                'p50': p50,
                'p90': p90,
                'p95': p95,
                '[bold]p99[/bold]': p99,
                'max': max(success_times),

            })
            
            if len(success_times) > 1:
                ep_analysis['stdev'] = statistics.stdev(success_times)

            # TODO mad: confirm with sel
            success = bool(p95 < threshold_p95)
            success &= bool(p99 < threshold_p99)

        else:
            success = False
        
        command_level_success &= success

        formatting = {
            "error_rate": ("{:.2f}%", None),
            "min_time": ("{:.2f}ms", None),
            "p50": ("{:.2f}ms", None),
            "p90": ("{:.2f}ms", None),
            "p95": ("{:.2f}ms", None),
            "[bold]p99[/bold]": ("[bold]{:.2f}ms[/bold]", None),
            "max": ("{:.2f}ms", None),
            "stdev": ("{:.2f}ms", None),
        }
         

        table = table_from_dict(
            ep_analysis, 
            "Metric", 
            "Value", 
            "",
            formatting,
            )
        
        plot = histogram(success_times)

        fmt_plot = Group(Text("\n"*1), plot)
        successes_columns = Columns([table, fmt_plot], equal=False, expand=True)

        if failures:
            failures_status_codes = collections.Counter([r["status_code"] for r in failures])        
            failures_table = table_from_dict(
                failures_status_codes, 
                "Status code of failed requests", 
                "N", 
                "",
                )
            panel_content = Group(successes_columns, failures_table)

        else:
            panel_content = Group(successes_columns)

        console.print(Panel(panel_content, title=f"{endpoint=}"))
    
    return command_level_success



def report_inspect(data: dict, code_threshold: int=300) -> bool:

    show_header = True
    table = Table(title="Line count", box=box.ROUNDED, show_header=show_header)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Code", justify="right")
    table.add_column("Docstring", justify="right")
    table.add_column("Other", justify="right")

    command_level_success = True
    for key, value in data.items():

        code, doc, other = value.get("code"), value.get("docstring"), value.get("other")
        success = code <= code_threshold
        emojy, msg, color, log_lvl = interpret(success)
        # lbl = f"[{color}]{key}[/{color}]"
        lbl = f"{key}"
        code, doc, other = str(code), str(doc), str(other)
        if not success:
            code = f"[{color}]{code}[/{color}]"
        row_values = [lbl, code,doc,other,]
        table.add_row(*row_values)

        command_level_success &= success

    console.print(table)

    return command_level_success

