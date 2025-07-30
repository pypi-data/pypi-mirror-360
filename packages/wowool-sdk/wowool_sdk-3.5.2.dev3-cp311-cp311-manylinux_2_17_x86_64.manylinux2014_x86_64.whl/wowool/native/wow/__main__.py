from wowool.wow import CLI as WowCommonCLI
from wowool.utility import is_valid_kwargs
import logging
from wowool.utility.method_registry import register
from wowool.io.console import console
from wowool.native.wow.argument_parser import ArgumentParser
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_arguments(*argv):
    """
    Parses the command line arguments.
    """

    parser = ArgumentParser()
    kwargs = parser.parse_args(*argv)
    return kwargs


class CLI(WowCommonCLI):
    def __init__(self, kwargs):
        super(CLI, self).__init__(kwargs)
        try:
            from wowool.native.core import Pipeline
            from wowool.native.core.engine import default_engine

            kwargs = kwargs | self.kwargs
            self.verbose = kwargs.get("verbose", "info")

            if is_valid_kwargs(kwargs, "lxware"):
                from wowool.native.core.engine import Engine

                self.engine = Engine(data=Path(kwargs["lxware"]).resolve())
            else:
                self.engine = default_engine()

            eng_info = self.engine.info()
            pipeline_options = {}
            if kwargs["dbg"]:
                pipeline_options["dbg"] = kwargs["dbg"]
            if kwargs["sentyziser"]:
                pipeline_options["sentyziser"] = kwargs["sentyziser"]

            allow_dev_version = kwargs["allow_dev_version"]
            pipeline_descriptor = kwargs["pipeline"]

            self.pipeline = Pipeline(
                pipeline_descriptor,
                paths=[eng_info["options"]["lxware"]],
                **pipeline_options,
                engine=self.engine,
                allow_dev_version=allow_dev_version,
            )
            assert hasattr(self, "pipeline") and self.pipeline is not None, "missing pipeline"
            self.filter = None
            if kwargs["annotations"]:
                from wowool.native.core import Filter

                self.filter = Filter(kwargs["annotations"])

            analyzer_arguments = {}
            domain_arguments = {}

            if "annotations" in kwargs and kwargs["annotations"] is not None:
                analyzer_arguments["annotations"] = kwargs["annotations"]

            if "utf8" not in kwargs or kwargs["utf8"] is True:
                analyzer_arguments["unicode_offset"] = False

            if "annotations" in kwargs and kwargs["annotations"] is not None:
                domain_arguments["annotations"] = kwargs["annotations"]

        except Exception as ex:
            if self.verbose == "debug" or self.verbose == "trace":
                logger.exception(f"Exception: {ex}")
            print(f"Exception: {ex}")
            exit(-1)

    @register()
    def info(self):
        from wowool.native.core import Domain

        cli = self
        prefix = " - "
        assert hasattr(cli, "pipeline") and cli.pipeline is not None, "missing pipeline"
        for component in cli.pipeline.components:
            print(component)
            if isinstance(component, Domain):
                info = component.info

                if "dom_info" in info and info["dom_info"]:
                    dom_info = info["dom_info"]

                    if "short_description" in dom_info:
                        console.print(f"""{prefix}short_description:{dom_info["short_description"]}""")

                if "dom" in info:
                    dom = info["dom"]
                    if "dom_filename" in dom:
                        console.print(f"""{prefix}dom: {dom["dom_filename"]}""")
                    if "dom_info_filename" in dom:
                        console.print(f"""{prefix}dom_info: {dom["dom_info_filename"]}""")
                    if "run_order" in dom:
                        console.print(f"{prefix}run_order:")
                        console.print_json(dom["run_order"])

                if "dom_info" in info:
                    dom_info = info["dom_info"]
                    if "dependencies" in dom_info:
                        console.print(f"{prefix}dependencies:")
                        console.print_json(dom_info["dependencies"])

                    if "concepts" in dom_info:
                        console.print(f"{prefix}concepts:")
                        console.print_json(dom_info["concepts"])

                    if "examples" in dom_info:
                        console.print(f"{prefix}examples:")
                        console.print_json(dom_info["examples"])


def main(*argv):
    import logging

    logging.basicConfig(level=logging.INFO)
    kwargs = dict(parse_arguments(*argv)._get_kwargs())
    driver = CLI(kwargs)
    driver.run()


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
