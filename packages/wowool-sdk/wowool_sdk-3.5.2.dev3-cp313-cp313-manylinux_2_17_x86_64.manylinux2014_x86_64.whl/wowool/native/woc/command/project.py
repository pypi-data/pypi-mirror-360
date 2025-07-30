import json
from pathlib import Path
from wowool.diagnostic import DiagnosticType
from wowool.native.woc.command.compile import command as compile

PROJECT_FILE_EXT = ".wopr"

COLOR_MAP = {
    DiagnosticType.Error: "red",
    DiagnosticType.Warning: "yellow",
    DiagnosticType.Info: "blue",
}


def fix_relative_path(fn_project, sources):
    project_root = fn_project.parent
    for idx, fn in enumerate(sources):
        pfn = Path(fn)
        if not pfn.exists():
            pfn = project_root / pfn
            if pfn.exists():
                sources[idx] = pfn
        else:
            sources[idx] = pfn


def command(**kwargs):
    assert kwargs["project"], "No project file specified"
    fn_project = Path(kwargs["project"])
    assert fn_project.exists(), f"Could not find project file {fn_project}"
    assert fn_project.exists(), "Project file does not exist"
    assert fn_project.suffix == PROJECT_FILE_EXT, f"Project file must have a {PROJECT_FILE_EXT} extension"
    with open(fn_project) as fh:
        project = json.load(fh)
        if "sources" in project:
            kwargs["sources"] = project["sources"]
        if "language" in project:
            kwargs["language"] = project["language"]
        if "domain" in project:
            kwargs["domain"] = project["domain"]
        dom_info = {}
        if "concepts" in project:
            dom_info["concepts"] = project["concepts"]
        if "dependencies" in project:
            dom_info["dependencies"] = project["dependencies"]
        if "short-description" in project:
            dom_info["short-description"] = project["short-description"]
        if "examples" in project:
            dom_info["examples"] = project["examples"]
        if "unknown_things" in project:
            dom_info["unknown_things"] = project["unknown_things"]
        if "instances" in project:
            dom_info["instances"] = project["instances"]
        if kwargs["output_file"] is None:
            if "output_file" in project:
                kwargs["output_file"] = project["output_file"]
            else:
                kwargs["output_file"] = fn_project.parent / Path(kwargs["domain"] + ".dom")

        if dom_info:
            dom_info_fn = Path(kwargs["output_file"]).with_suffix(".dom_info")
            with open(dom_info_fn, "w") as fh:
                print(f"Generating dom_info file: {dom_info_fn}")
                json.dump(dom_info, fh)

        fix_relative_path(fn_project, project["sources"])

    # domain_name = kwargs["domain"]
    # kwargs["output_file"]
    # language = kwargs["language"]
    # wow_files = kwargs["sources"]
    kwargs["input_files"] = kwargs["sources"]
    return compile(**kwargs)
