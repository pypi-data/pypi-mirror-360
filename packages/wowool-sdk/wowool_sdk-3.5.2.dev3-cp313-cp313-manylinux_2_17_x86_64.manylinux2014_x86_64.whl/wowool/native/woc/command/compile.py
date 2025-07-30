from pathlib import Path
from wowool.io.console import console
from wowool.diagnostic import DiagnosticType
from wowool.native.core.compiler import Compiler
from wowool.error import Error as CompilerError
from argparse import ArgumentError

PROJECT_FILE_EXT = ".wopr"

COLOR_MAP = {
    DiagnosticType.Error: "red",
    DiagnosticType.Warning: "yellow",
    DiagnosticType.Info: "blue",
}


color_map = {"error": "red", "warning": "yellow", "note": "blue"}


def print_results(results):
    indent = " " * 11
    if "sink" in results._results:
        for sink_id, sink in results._results["sink"].items():
            file_prefix = " " * len(sink_id)
            for dia in sink:
                color = color_map[dia["type"]] if dia["type"] in color_map else ""
                if dia["type"] == "error_marker":
                    console.print(f"{indent}{file_prefix} {dia['msg']}")
                elif "line" in dia:
                    error_code = f""":(0x{dia['code']:x})""" if "code" in dia else ""
                    console.print(f"{sink_id}:{dia['line']}:{dia['column']}: [{color}]{dia['type']}[/{color}]{error_code} {dia['msg']}")
                else:
                    console.print(f"{sink_id}:{dia['type']} {dia['msg']}")
    if "message" in results._results:
        console.print(results._results["message"])


def command(output_file: str, input_files: list[Path | str], **kwargs):
    try:
        compiler_arguments = {**kwargs}

        for wfn in input_files:
            if str(wfn) in kwargs.keys():
                raise ArgumentError(None, message=f"it should have been --{wfn}")
            if not Path(wfn).exists():
                raise ValueError(f"Input file '{wfn}' not found.")

        if "unit_test" in kwargs:
            if kwargs["unit_test"] is True:
                compiler_arguments["unit_test"] = True

        if kwargs["language"] is None:
            kwargs.pop("language")

        if "sources" in compiler_arguments:
            del compiler_arguments["sources"]
        del compiler_arguments["version"]
        if "project" in compiler_arguments:
            del compiler_arguments["project"]
        if "create" in compiler_arguments:
            del compiler_arguments["create"]
        if "domain" in compiler_arguments:
            del compiler_arguments["domain"]

        if "ignore_codes" not in compiler_arguments or compiler_arguments["ignore_codes"] is None:
            compiler_arguments["ignore_codes"] = 0

        results = Compiler.compile(output_file=output_file, input_files=input_files, **compiler_arguments)

        print_results(results)

        if results.status:
            return 0
        else:
            return -1

    except CompilerError as ex:
        print(f"{ex}")
        return -1
