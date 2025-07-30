import os
import sys
import json
from pathlib import Path
from xmlrpc.client import boolean
import wowool.package.lib.wowool_sdk as cpp
from wowool.error import Error
from typing import Callable, Union, List, Optional


# TODO: move to core-io
def _escape_windows_paths(path):
    path_str = json.JSONEncoder().encode(str(Path(path).resolve()))[1:-1]
    return path_str


class Results:
    """
    Results object representing the compilation output.

    .. literalinclude:: english_compiler_error.py
        :caption: english_compiler_save.py

    .. literalinclude:: english_compiler_error_output_no_diff.txt

    """

    def __init__(self, json_data):
        self.json_data = json_data
        self._results = json.loads(self.json_data)

    @property
    def status(self):
        """
        Return whether the domain was successfully compiled
        """
        return self._results["return"]

    @property
    def sink(self):
        """
        Return an error sink. Format of the sink is:

        .. code-block:: json

            {
                "test.wow" : [
                    {
                        "type": "error",
                        "line": 1,
                        "column":8,
                        "msg": "Missing ':' after keyword"
                    }
                ]
            }

        """
        return self._results["sink"]

    def diagnostics(self):
        from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType

        diagnostics = Diagnostics()
        if "sink" in self._results:
            for sink_id, sink in self._results["sink"].items():
                for error in sink:
                    if error["type"] == "error_marker":
                        pass
                    type = DiagnosticType.Error
                    if error["type"] == "warning":
                        type = DiagnosticType.Warning
                    elif error["type"] == "note":
                        type = DiagnosticType.Info

                    if "line" in error:
                        diagnostics.add(Diagnostic(sink_id, f"{error['line']}:{error['column']}: {error['type']} {error['msg']}", type))
                    else:
                        diagnostics.add(Diagnostic(sink_id, f"{error['type']} {error['msg']}", type))

            if "message" in self._results:
                diagnostics.add(Diagnostic("main", self._results["message"], DiagnosticType.Info))

    def __str__(self):
        from io import StringIO

        with StringIO() as output:
            indent = " " * 11
            if "sink" in self._results:
                for sink_id, sink in self._results["sink"].items():
                    file_prefix = " " * len(sink_id)
                    for error in sink:
                        if error["type"] == "error_marker":
                            output.write(f"{indent}{file_prefix} {error['msg']}\n")
                        elif "line" in error:
                            output.write(f"{sink_id}:{error['line']}:{error['column']}: {error['type']} {error['msg']}\n")
                        else:
                            output.write(f"{sink_id}:{error['type']} {error['msg']}\n")
            if "message" in self._results:
                output.write(self._results["message"])
            return output.getvalue()


def logit(id: int, msg: str):
    print(msg, file=sys.stderr)


class Compiler:
    """
    A Compiler object can be used to compile rules or lexicons to an existing domain object.

    .. literalinclude:: english_compiler_init.py
        :caption: english_compiler_init.py


    A domain object can also be used to build a .dom file from either source files or input data.

    .. code-block:: python
        :linenos:

        from wowool.native.core import Compiler

            d = Compiler( )
            d.add_source( r\"\"\" rule:{ Person .. <'work'> .. Company }= PersonWorkCompany;\"\"\" )
            d.add_source( r\"\"\" rule:{ Person .. Company }= PersonCompany;\"\"\" )
            results = d.save('profile.dom')
            if not results.status:
                print(results)

    """

    @staticmethod
    def compile(
        output_file: Union[str, Path],
        input_files: Optional[Union[List[str], List[Path]]] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        force: boolean = False,
        unit_test: boolean = False,
        strict: boolean = False,
        threads: int = 4,
        verbose: str = "fatal",
        parse_only: boolean = False,
        ignore_codes: int = 0,
        disable_plugin_calls: bool = False,
        lxware: Optional[str] = None,
        logger_function: Callable[[int, str], None] = None,
    ) -> Results:
        """
        Compile a given domain file.

        :param output_file: Output file name of the domain ex: 'drinks.dom'
        :type output_file: [str,Path]
        :param input_files: List of wow file to compile, ex: [ "beers.wow" , "wine.dom" ]
        :type input_files: list[str, Path]
        :param source: Wowoolian source code.
        :type source: str
        :param language: The language to use for the unit-tests
        :type language: str
        :param force: Force a full build
        :type force: boolean
        :param unit_test: Perform unit-test on the source file that contains @test arguments
        :type unit_test: boolean
        :param verbose:
        :type verbose: str
        :param strict: Perform strict parsing of the wowool language.
        :type strict: boolean

        .. code-block:: python

            from wowool.native.core import Compiler

            # Build your domain.
            Compiler.compile( input_files=['test.wow'] , output_file='car.dom' )

        """
        try:
            compiler_arguments = {}

            # take care to escape windows paths otherwise the json will no be valid.
            compiler_arguments["output_file"] = _escape_windows_paths(output_file)
            if input_files:
                compiler_arguments["input_files"] = ",".join([_escape_windows_paths(str(fn)) for fn in input_files])

            compiler_arguments["force"] = force
            compiler_arguments["strict"] = strict
            compiler_arguments["unit_test"] = unit_test
            if language:
                compiler_arguments["language"] = language
            compiler_arguments["threads"] = threads
            compiler_arguments["tag_output"] = True
            compiler_arguments["parse_only"] = parse_only
            compiler_arguments["ignore_codes"] = ignore_codes
            compiler_arguments["disable_plugin_calls"] = disable_plugin_calls
            if lxware:
                compiler_arguments["lxware"] = lxware

            if source is not None:
                if len(source):
                    import base64

                    compiler_arguments["wow_base64"] = base64.b64encode(source.encode()).decode("utf-8")

            if logger_function:
                cpp.add_logger(0x1000, verbose, logger_function)
            try:
                return Results(cpp.compile_domain("", compiler_arguments))
            except (Exception, cpp.TirException) as error:
                raise Error(error).with_traceback(sys.exc_info()[2])

        finally:
            cpp.unset_logger()

    def __init__(self):
        """Instantiate a `Compiler` object"""
        self._sources = []
        self._files = []

    def add_source(self, source: str):
        """
        Add wow source code to the domain object.

        :param source: wowool source code.
        :type source: str

        """
        self._sources.append(source)

    def add_file(self, wow_file: str):
        """
        Add a wow file.
        A domain object is used to build a .dom file from either source files or input data.
        """
        wow_file = str(wow_file)

        if not os.path.isfile(wow_file):
            raise Error(f"Input file does not exists [{wow_file}]")
        assert os.path.isfile(wow_file), f"Input file does not exists [{wow_file}]"
        self._files.append(wow_file)

    # TODO: refactor filenames code
    def save(self, output_filename, parse_only=False, disable_plugin_calls=False, logger_function: Callable[[int, str], None] = None):
        """
        Save the files or sources that have been added to the domain.

        :param output_filename: The domain (.dom) filename.
        :type output_filename: [str,Path]
        :param parse_only: Will not generate a dom file, but will only perform syntax checking.
        :type parse_only: boolean

        .. literalinclude:: english_compiler_save.py
            :caption: english_compiler_save.py

        .. literalinclude:: english_compiler_save_output.txt

        """
        wow_opt = {"output_file": _escape_windows_paths(output_filename), "verbose": "fatal"}
        wow_source_data = ""
        for wow_source in self._sources:
            wow_source_data += wow_source + " "

        if len(wow_source_data):
            import base64

            wow_opt["wow_base64"] = base64.b64encode(wow_source_data.encode()).decode("utf-8")

        filenames = ",".join(self._files)
        if len(filenames):
            wow_opt["input_files"] = _escape_windows_paths(filenames)

        if parse_only:
            wow_opt["parse_only"] = True

        if disable_plugin_calls:
            wow_opt["disable_plugin_calls"] = True

        fn_out = Path(output_filename).resolve()
        if fn_out.exists():
            fn_out.unlink()

        try:
            return Results(cpp.compile_domain("", wow_opt))
        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(sys.exc_info()[2])
