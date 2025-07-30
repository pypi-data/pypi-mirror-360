import os
from pathlib import Path
from sysconfig import get_config_var
import setuptools
from setuptools.command.build_ext import build_ext
from wheel.bdist_wheel import bdist_wheel
import platform
from setuptools import setup, Extension
import logging
import sys
from subprocess import run
from setuptools.command.build_py import build_py as _build_py

logger = logging.getLogger(__name__)

logger.debug(f"Python version: {sys.version}")

# Ensure pre_build.py is in the same directory as setup.py
if not os.path.exists("pre_setup.py"):
    raise FileNotFoundError("pre_setup.py not found in the same directory as setup.py")

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from pre_setup import prep_build_setup, post_build_setup, get_origin_keyword  # noqa: E402


def _get_machine_name():
    """
    Returns the machine architecture name in Docker-compatible format
    """
    machine = platform.machine().lower()

    # Map from system architecture names to Docker platform names
    docker_arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "i386": "386",
        "i686": "386",
        "aarch64": "arm64",
        "arm64": "arm64",
        "armv7l": "arm/v7",
        "armv6l": "arm/v6",
        "s390x": "s390x",
        "ppc64le": "ppc64le",
        "ppc64": "ppc64",
    }

    return docker_arch_map.get(machine, machine)


def _get_system_name():
    platform_name = platform.system()
    if "Linux" == platform_name:
        return f"{platform.system()}-{_get_machine_name()}-{platform.libc_ver()[0]}"
    elif "Darwin" == platform_name:
        return f"{platform.system()}-{_get_machine_name()}"
    elif "Windows" == platform_name:
        return f"{platform.system()}-{_get_machine_name()}-{platform.win32_ver()[0]}"


def get_folders(this_folder: Path, system_name: str):

    local_stage = os.environ.get("WOWOOL_USE_LOCAL_STAGE", False)
    print("Stage folder:", local_stage)
    if isinstance(local_stage, str) and local_stage.lower() == "true":
        stage_folder = Path(local_stage)
        stage_folder = this_folder / "stage"
    else:
        stage_folder = this_folder / system_name / "stage"
        stage_folder.mkdir(parents=True, exist_ok=True)

    bin_folders = stage_folder / "bin"
    lib_folders = stage_folder / "lib"
    inc_folders = stage_folder / "cpp" / "inc" / "wowool"
    return stage_folder, bin_folders, lib_folders, inc_folders


SYSTEM_NAME = _get_system_name()
REPO_NAMESPACE = f"tir-{SYSTEM_NAME}"

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

try:
    from setuptools import find_namespace_packages

    wowool_packages = None
except ImportError:
    wowool_packages = [
        "wowool",
        "wowool.native",
        "wowool.plugin",
        "wowool.package",
        "wowool.lxware",
        "wowool.package.bin",
        "wowool.package.lib",
    ]


def platform_info():
    return _get_system_name()


def download_http_file(nexus_uri, output_folder, filename, username, password):
    import urllib.request

    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, nexus_uri, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib.request.build_opener(handler)
    # use the opener to fetch a URL
    fn = Path(output_folder) / filename
    u = opener.open(nexus_uri)
    with open(fn, "w+b") as fh:
        fh.write(u.read())  # Returns http.client.HTTPResponse.

    if not fn.is_file():
        logger.critical(f"Was not able to download {filename} from nexus into {output_folder}")
        exit(-1)


def download_raw(version: str, file_name: str, output_path: Path):
    """
    Download a raw asset from a GitHub release

    Args:
        repo: GitHub repository in format 'username/repo'
        version: Release tag version
        file_name: Name of the asset to download
        output_path: Path where to save the downloaded file
    """
    import requests

    repo = "wowool/wowool_sdk_cpp_release"
    # GITHUB_TOKEN = environ.get("GITHUB_TOKEN")
    # headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # ==== STEP 1: Get the release info ====
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/{version}"
    release_resp = requests.get(release_url)
    # release_resp = requests.get(release_url, headers=headers)
    release_resp.raise_for_status()
    release_data = release_resp.json()
    print(f"📦 Found release: {release_data['name']} (ID: {release_data['id']})")

    asset_url = None
    for asset in release_data.get("assets", []):
        if asset["name"] == file_name:
            asset_url = asset["browser_download_url"]
            print(f"📄 Found asset: {file_name}")
            break

    if not asset_url:
        available_assets = ", ".join([asset["name"] for asset in release_data.get("assets", [])])
        raise ValueError(f"Asset '{file_name}' not found in release. Available assets: {available_assets}")

    # ==== STEP 3: Download the asset ====
    # download_headers = headers.copy()
    # download_headers.update({"Accept": "application/octet-stream"})

    # download_resp = requests.get(asset_url, headers=download_headers, stream=True)
    download_resp = requests.get(asset_url, stream=True)
    download_resp.raise_for_status()

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    with open(output_path, "wb") as f:
        for chunk in download_resp.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded {file_name} to {output_path}")
    return output_path


def download_file(output_filename: Path, wow_sdk_version):

    # the codeartifact is a local file and not the one in core build
    print(f"Downloading {output_filename} from {wow_sdk_version}")
    download_raw(file_name=output_filename.name, output_path=output_filename, version=wow_sdk_version)


def get_site_packages_dir():
    import site

    return [p for p in site.getsitepackages() if "site-packages" in p or "dist-packages" in p][0]


def extract_archive(file_path, archive_folder):
    import shutil

    if archive_folder.is_dir():
        shutil.rmtree(str(archive_folder))
    archive_folder.mkdir()

    cmd = f"tar -xvf {file_path} -C {str(archive_folder)} --strip-components=1"
    run(cmd, shell=True, check=True)
    for fn in archive_folder.glob("**/*"):
        print(f"[EOT] - {fn}")


WOWOOL_STAGE, bin_folders, lib_folders, inc_folders = get_folders(Path(__file__).parent.resolve(), SYSTEM_NAME)


def is_valid_stage_folder(folder: Path):
    if not folder.is_dir():
        return False
    if not (folder / "bin").is_dir():
        return False
    if not (folder / "lib").is_dir():
        return False
    if not (folder / "cpp" / "inc" / "wowool").is_dir():
        return False
    return True


def check_stage():

    print(f"[WOW] check_stage: {WOWOOL_STAGE=} {lib_folders=} {inc_folders=}")
    THIS_DIR = Path(__file__).parent.resolve()

    if is_valid_stage_folder(WOWOOL_STAGE):
        print(f"[WOW] already: {WOWOOL_STAGE=}")
        wow_sdk_folder = WOWOOL_STAGE
        # common_setup.copy_to_package_folder(THIS_DIR, wow_sdk_folder, bin_folders, inc_folders, lib_folders)

    else:
        if "WOWOOL_USE_LOCAL_STAGE" in os.environ and os.environ["WOWOOL_USE_LOCAL_STAGE"].lower() == "true":
            raise RuntimeError("WOWOOL_USE_LOCAL_STAGE is set to True, but the WOWOOL_STAGE is not valid.")

        print(f"[WOW] download: {WOWOOL_STAGE=}")
        # download and exrtact the wow-sdk
        if "WOWOOL_SDK_VERSION" in os.environ:
            native_cpp_sdk_version = os.environ["WOWOOL_SDK_VERSION"]
        else:
            sdk_version_fn = Path(__file__).parent / "sdk_version.txt"
            if sdk_version_fn.exists():
                with open(sdk_version_fn) as fh:
                    native_cpp_sdk_version = fh.read().strip()

        platform_name = os.environ["WOWOOL_PLATFORM_NAME"] if "WOWOOL_PLATFORM_NAME" in os.environ else platform_info()
        extension = "tar.gz" if platform.system() != "Windows" else "zip"
        native_cpp_sdk_tgz = f"wow-sdk-{native_cpp_sdk_version}-{platform_name}-core.{extension}"
        try:

            if not (THIS_DIR / native_cpp_sdk_tgz).exists():
                download_file(THIS_DIR / native_cpp_sdk_tgz, wow_sdk_version=native_cpp_sdk_version)

            full_native_cpp_sdk_tgz = THIS_DIR / native_cpp_sdk_tgz
            logger.info(f"[WOW] {full_native_cpp_sdk_tgz=}")
            print(f"[WOW] extract_archive: {full_native_cpp_sdk_tgz=}:{full_native_cpp_sdk_tgz.exists()=}")
            wow_sdk_folder = WOWOOL_STAGE

            extract_archive(THIS_DIR / native_cpp_sdk_tgz, wow_sdk_folder)
        except Exception as ex:
            print(
                f"""[WOWOOL] {ex} Could not downloaded or extract the requested package.
    You will need to set the WOWOOL_STAGE folder, to build the native package."""
            )


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked."""

    def __str__(self):
        import pybind11

        return pybind11.get_include()


def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    import os

    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False) as f:
        f.write("int main (int argc, char **argv) { return 0; }")
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except setuptools.distutils.errors.CompileError:
        return False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.

    The newer version is preferred over c++11 (when it is available).
    """
    flags = ["-std=c++17", "-std=c++14", "-std=c++11"]

    for flag in flags:
        if has_flag(compiler, flag):
            return flag

    raise RuntimeError("Unsupported compiler -- at least C++11 support " "is needed!")


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/EHsc"],
        "unix": [],
    }
    l_opts = {
        "msvc": [],
        "unix": [],
    }

    if sys.platform == "darwin":
        darwin_opts = ["-stdlib=libc++", "-mmacosx-version-min=11.0"]
        c_opts["unix"] += darwin_opts
        l_opts["unix"] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == "unix":
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, "-fvisibility=hidden"):
                opts.append("-fvisibility=hidden")

        for ext in self.extensions:
            ext.define_macros = [("VERSION_INFO", '"{}"'.format(self.distribution.get_version()))]
            ext.extra_compile_args.extend(opts)
            ext.extra_link_args.extend(link_opts)
            if ct == "msvc":
                if "runtime_library_dirs" in ext.extra_link_args:
                    del ext.extra_link_args["runtime_library_dirs"]
        build_ext.build_extensions(self)


wowool_plugin_hpp_file = Path("src/plugin/wowool_plugin.hpp")


def support_cpp_plugin_build():
    retval = "WOWOOL_CPP_BUILD_SUPPORT" in os.environ and os.environ["WOWOOL_CPP_BUILD_SUPPORT"] == "True"
    print(f"! Adding CPP Drive support. {retval}")
    return retval


def extension_modules():
    import sysconfig

    print("WOWOOL_STAGE", WOWOOL_STAGE)
    # Note do NOT .resolve() the paths
    _wowool_cpp_file = Path("wowool/native/core/wowool_sdk.cpp")
    wowool_plugin_cpp_file = Path("wowool/plugin/wowool_plugin.cpp")

    extra_compile_args = sysconfig.get_config_var("CFLAGS").split() if sysconfig.get_config_var("CFLAGS") else []
    extra_link_args = sysconfig.get_config_var("LDFLAGS").split() if sysconfig.get_config_var("LDFLAGS") else []

    if "WOWOOL_PLUGIN_LDFLAGS" in os.environ:
        extra_link_args.extend(os.environ["WOWOOL_PLUGIN_LDFLAGS"].split(" "))
    if "WOWOOL_PLUGIN_CPPFLAGS" in os.environ:
        extra_compile_args.extend(os.environ["WOWOOL_PLUGIN_CPPFLAGS"].split(" "))

    runtime_library_path = str(Path(WOWOOL_STAGE, "lib"))
    if sys.platform == "darwin":
        version_int = int(platform.mac_ver()[0].split(".")[0])
        runtime_library_dirs = [runtime_library_path]
        if version_int >= 12:
            extra_link_args.extend(
                [
                    "-Xlinker",
                    "-syslibroot",
                    "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk",
                ]
            )
        extra_compile_args.extend(["-arch", "arm64", "-arch", "x86_64"])
        extra_link_args.extend(["-arch", "arm64", "-arch", "x86_64"])
        extra_link_args.extend(["-Xlinker", "-rpath", "-Xlinker", get_origin_keyword()])
        # We include the python library to build a library that works for the cpp build
        libraries = ["wowool"]
        plugin_libraries = [get_config_var("LIBRARY")[3:-2], "wowool"] if support_cpp_plugin_build() else ["wowool"]
        library_dirs = [str(Path(WOWOOL_STAGE, "lib")), get_config_var("LIBDIR")]
        # We use to include the python library, but it causes issues when using the
        # regular python installation, (not using brew)
        if version_int >= 12:
            extra_compile_args.extend(
                ["-isysroot", "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"]
            )

    elif sys.platform == "win32":
        runtime_library_dirs = []
        extra_link_args = []
        library_dirs = [str(Path(WOWOOL_STAGE, "lib")), get_config_var("LIBDEST")]
        libraries = ["wowool"]
        plugin_libraries = libraries
    else:
        runtime_library_dirs = [runtime_library_path]
        extra_link_args = ["-Xlinker", "-rpath", "-Xlinker", get_origin_keyword(), "-static-libstdc++"]
        library_dirs = [str(Path(WOWOOL_STAGE, "lib")), get_config_var("LIBDIR")]
        libraries = ["wowool"]
        plugin_libraries = [get_config_var("LIBRARY")[3:-2], "wowool"] if support_cpp_plugin_build() else ["wowool"]

    if "WOWOOL_PLUGIN_LIBRARIES" in os.environ:
        libraries.extend(os.environ["WOWOOL_PLUGIN_LIBRARIES"].split(" "))

    return [
        Extension(
            "wowool.package.lib._wowool_sdk",
            [str(_wowool_cpp_file)],
            include_dirs=[str(Path(WOWOOL_STAGE, "cpp", "inc")), get_pybind_include()],
            library_dirs=library_dirs,
            libraries=libraries,
            language="c++",
            runtime_library_dirs=runtime_library_dirs,
            extra_link_args=extra_link_args,
            extra_compile_args=extra_compile_args,
        ),
        Extension(
            "wowool.package.lib._wowool_plugin",
            [str(wowool_plugin_cpp_file)],
            # [str(wowool_plugin_cpp_file), str(wowool_plugin_module_cpp_file)],
            include_dirs=[
                str(Path(WOWOOL_STAGE, "cpp", "inc")),
                "/wowool/plugin",
                get_pybind_include(),
            ],
            library_dirs=library_dirs,
            libraries=plugin_libraries,
            language="c++",
            runtime_library_dirs=runtime_library_dirs,
            extra_link_args=extra_link_args,
            extra_compile_args=extra_compile_args,
        ),
    ]


long_description = (Path(__file__).parent / "long_description.md").read_text()

if not wowool_packages:
    wowool_packages = find_namespace_packages(include=["wowool.*"])


package_name = "wowool-sdk"


class CustomBuildPyCommand(_build_py):
    """Custom build command to run pre-build setup."""

    def run(self):
        self.prep_build_setup()
        _build_py.run(self)

    def prep_build_setup(self):
        # Add your pre-build setup code here
        check_stage()
        prep_build_setup(WOWOOL_STAGE)


class CustomBdistWheel(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()

    def run(self):
        super().run()
        # Post-wheel creation code here
        print("Wheel has been created, running post-processing")
        post_build_setup(WOWOOL_STAGE)


install_requires = [
    requirement.strip()
    for requirement in open("install_requires.txt").readlines() + open("install_requires_wowool.txt").readlines()
    if requirement.strip()
]
version = open("version.txt").read().strip()


results = setup(
    name=package_name,
    version=version,
    author="Wowool",
    description="Wowool NLP Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    setup_requires=["pybind11"],
    packages=wowool_packages,
    ext_modules=extension_modules(),
    cmdclass={"build_py": CustomBuildPyCommand, "build_ext": BuildExt, "bdist_wheel": CustomBdistWheel},
    python_requires=">=3.11",
    zip_safe=False,
    package_data={
        "wowool.package.lib": ["*"],
        "wowool.plugin": ["wowool_plugin.hpp"],
    },
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "wow = wowool.native.wow.__main__:main",
            "wow++ = wowool.native.wow_cpp:main",
            "woc = wowool.native.woc.__main__:main",
            "woc++ = wowool.native.woc_cpp:main",
            "afst++ = wowool.native.afst_cpp:main",
            "wow.cp = wowool.native.wow_copy.__main__:main",
            "create_locale_language = wowool.native.create_locale_language.__main__:main",
        ]
    },
)
