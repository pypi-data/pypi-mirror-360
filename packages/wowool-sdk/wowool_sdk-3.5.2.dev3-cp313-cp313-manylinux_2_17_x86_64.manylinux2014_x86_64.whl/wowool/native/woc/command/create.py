from pathlib import Path
import os
from wowool.io.console import console
from wowool.tool.woc.create import create_project


def command(create, language, **kwargs):
    fn_project = Path(create)
    language = language if language else "english"
    fn_project = create_project(fn_project, language=language)
    console.print(f"Created project file: {fn_project}")
    console.print(fn_project.read_text())
    console.print(
        f"To compile, run the following:\n  woc --project {fn_project.relative_to(os.getcwd())}"
    )
    return 0
