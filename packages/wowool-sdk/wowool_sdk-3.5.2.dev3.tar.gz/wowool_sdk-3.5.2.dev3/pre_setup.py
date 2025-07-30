import os
import shutil
from pathlib import Path
import platform
from logging import getLogger
import subprocess
import json

logger = getLogger(__name__)

this_dir = Path(__file__).parent
fusion_root = None
fusion_root = this_dir

pi = platform.system()
tar_ext = "tar.gz" if pi != "Windows" else "zip"
app_ext = "" if pi != "Windows" else ".exe"
SO_EXT = ".so" if pi != "Windows" else ".pyd"
native_so_prefix = "lib" if pi != "Windows" else ""
if pi == "Windows":
    NATIVE_SO_EXT = ".dll"
elif pi == "Darwin":
    NATIVE_SO_EXT = ".dylib"
else:
    NATIVE_SO_EXT = ".so"


def get_origin_keyword():
    if platform.system() == "Darwin":
        return "@loader_path"
    elif platform.system() == "Linux":
        return "$ORIGIN"


def call_subprocess(cmd_params):
    cmd = " ".join(cmd_params)
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as ex:
        logger.exception(f"Cannot run [{cmd}], {ex}")


def get_all_rpaths(filename):
    if platform.system() == "Darwin":
        cmd = ["otool", "-l", str(filename)]
        if not filename.exists():
            raise RuntimeError(f"File not there yet {filename}")
        rpathlist = [line.strip() for line in subprocess.check_output(cmd).decode().split("\n")]
        rpaths = []
        pidx = -1
        for idx, line in enumerate(rpathlist):
            if line.startswith("cmd LC_RPATH"):
                pidx = idx + 2
            elif idx == pidx:
                rpaths.append(line.split(" ")[1])
        return rpaths
    else:
        assert False, "Not implemented for given platform."


def remove_all_build_rpaths(filename):
    if platform.system() == "Darwin":
        build_paths = get_all_rpaths(filename)
        for build_path in build_paths:
            try:
                cmd_params = ["install_name_tool", "-delete_rpath", str(build_path), str(filename)]
                call_subprocess(cmd_params)
            except Exception as ex:
                logger.error(f"Failed to remove rpath {build_path} from {filename}: {ex}")
                pass

        assert len(get_all_rpaths(filename)) == 0


def remove_rpath(filename):
    if platform.system() == "Darwin":
        remove_all_build_rpaths(filename)
    elif platform.system() == "Linux":
        cmd_params = [
            "patchelf",
            "--remove-rpath",
            str(filename),
        ]
        call_subprocess(cmd_params)


def set_rpath_origin(filename):
    if platform.system() == "Darwin":
        cmd_params = ["install_name_tool", "-add_rpath", get_origin_keyword(), str(filename)]
        call_subprocess(cmd_params)
    elif platform.system() == "Linux":
        cmd_params = [
            "patchelf",
            "--force-rpath",
            "--set-rpath",
            f"\\{get_origin_keyword()}",
            str(filename),
        ]
        call_subprocess(cmd_params)


def prep_build_setup(wow_stage: Path):
    """
    Prepare the source folders
    """
    logger.info(f"----------------- begin prepping {wow_stage}---------------------")

    this_repo = Path(this_dir)
    package_lxware_folder = this_repo / "wowool" / "package" / "lxware"
    package_lib_folder = this_repo / "wowool" / "package" / "lib"

    logger.debug(f"{this_repo}")

    os.makedirs(package_lxware_folder, exist_ok=True)

    stage_bin_folder = wow_stage / "bin"
    stage_lib_folder = wow_stage / "lib"

    icu_lib_folder = stage_lib_folder

    tir_config_fn = wow_stage / "config.json"
    if tir_config_fn.exists():
        with open(tir_config_fn) as fh:
            tir_config = json.load(fh)
            TIR_VERSION = tir_config["version"]

        sdk_version_fn = this_dir / "sdk_version.txt"
        with open(sdk_version_fn) as fh:
            current_sdk_version = fh.read().strip()

        if current_sdk_version != TIR_VERSION:
            raise ValueError(
                f"""!!! The native python SDK requires version'{current_sdk_version}' of the cpp SDK, but found the version '{TIR_VERSION}' in {stage_lib_folder}\nChange {sdk_version_fn.stem}"""
            )
    else:
        assert fusion_root
        tir_version = this_dir / "sdk_version.txt"
        if tir_version.exists():
            with open(tir_version, "r") as fh:
                TIR_VERSION = fh.read().strip()
        else:
            TIR_VERSION = os.environ["TIR_VERSION"]

    # change the rpath for the end package to used $ORIGIN
    pattern = f"*{NATIVE_SO_EXT}"
    native_linux_pattern = f"*{NATIVE_SO_EXT}.{TIR_VERSION}"

    platform_name = platform.system()
    if "Windows" == platform_name:
        icu_files = ["icudt.lib", "icuuc.lib"]
    elif "Darwin" == platform_name:
        icu_files = ["libicudata.dylib", "libicuuc.dylib"]
    else:
        icu_files = ["libicudata.so", "libicuuc.so"]

    logger.info(f"{TIR_VERSION=} {package_lib_folder=} {native_linux_pattern=}")

    for fn in stage_lib_folder.glob(native_linux_pattern):
        target_fn = package_lib_folder / fn.name
        logger.info(f"copy 1 {fn} --> {target_fn}")

        if fn.is_symlink():
            continue
        shutil.copy2(fn, target_fn)
        # remove_rpath(target_fn)
        # set_rpath_origin(target_fn)

    logger.info(f"copy {stage_lib_folder=}")
    for fn in stage_lib_folder.glob(pattern):
        target_fn = package_lib_folder / fn.name
        if target_fn.name.startswith("_"):
            continue
        if fn.is_symlink():
            # do not copy symlinks.
            # shutil.copy2(fn, package_lib_folder / fn.name , follow_symlinks=False )
            pass
        else:
            if target_fn.exists():
                target_fn.unlink()
            target_fn.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"copy2 {fn} --> {target_fn}")
            shutil.copy2(fn, target_fn)

    # copy icu
    logger.info("----------------- before ---------------------")
    for fn in package_lib_folder.glob("**/*"):
        logger.info(f"package: {fn}")

    for fn in icu_files:
        target_fn = package_lib_folder / fn
        shutil.copy2(icu_lib_folder / fn, target_fn)
        # remove_rpath(target_fn)
        # set_rpath_origin(target_fn)

    if "Windows" == platform_name:
        # for windows we also need to copy the dll
        bin_files = [[fn] for fn in stage_bin_folder.glob("*.dll")]
        bin_files.append([stage_bin_folder / "wow.exe", "wow++.exe"])
        bin_files.append([stage_bin_folder / "woc.exe", "woc++.exe"])
        bin_files.append([stage_bin_folder / "afst.exe", "afst++.exe"])
    else:
        bin_files = []
        bin_files.append([stage_bin_folder / "wow", "wow++"])
        bin_files.append([stage_bin_folder / "woc", "woc++"])
        bin_files.append([stage_bin_folder / "afst", "afst++"])

    for fn in bin_files:
        if len(fn) == 1:
            target_fn = package_lib_folder / fn[0].name
        else:
            target_fn = package_lib_folder / fn[1]

        shutil.copy2(fn[0], target_fn)
        remove_rpath(target_fn)
        logger.info(f"set_rpath_origin {target_fn}")
        set_rpath_origin(target_fn)
    logger.info("----------------- end prepping ---------------------")
    for fn in package_lib_folder.glob("**/*"):
        if "__pycache_" not in str(fn):
            logger.info(f"package: {fn}")


def post_build_setup(stage: Path):
    """
    Prepare the source folders
    """

    print("post_build ... ")

    files = [fn for fn in stage.glob(f"lib/*{NATIVE_SO_EXT}")]
    for fn in files:
        remove_rpath(fn)
        set_rpath_origin(fn)
