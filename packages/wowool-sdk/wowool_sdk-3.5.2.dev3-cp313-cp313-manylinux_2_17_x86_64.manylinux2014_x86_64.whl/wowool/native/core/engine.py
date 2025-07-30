import json
import os
import wowool.package.lib.wowool_sdk as cpp
from pathlib import Path
from functools import wraps
from typing import Union, Callable, Dict, Tuple, List
import atexit
from wowool.native.core.component_info import ComponentInfo


def _generate_language_maps(_language_info) -> Tuple[Dict[str, str], Dict[str, str]]:
    l2c = {}
    c2l = {}
    # ln = language name
    for ln, data in _language_info.items():
        if "code" in data:
            code = data["code"]
            l2c[ln] = code
            c2l[code] = ln

    return l2c, c2l


def check_language_info(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert self._cpp is not None
        if not self._language_info:
            self._language_info = json.loads(self._cpp.languages())
            self._languages = frozenset(self._language_info.keys())
            self._language_to_code, self._code_to_language = _generate_language_maps(self._language_info)

        return func(self, *args, **kwargs)

    return wrapper


class Engine:
    """Engine is a class that keeps important information loaded into memory and shares it with the Languages and the Domains"""

    def __init__(self, data=None, lxware=None, **kwargs):
        options = {}
        if data:
            options["lxware"] = data
        if lxware:
            options["lxware"] = lxware
        if kwargs:
            for key, value in kwargs.items():
                options[key] = value
        options["pytryoshka"] = True

        self._cpp = cpp.engine(options)

        info = self.info()

        assert "options" in info and "lxware" in info["options"], "lxware option not in path not found !"
        self._lxware = [Path(pth) for pth in info["options"]["lxware"].split(os.pathsep)]
        assert len(self._lxware), "No lxware paths found in lxware options"
        assert self._lxware[0].exists(), f"Path does not exists, {self._lxware[0]}"
        self._lib = Path(self._lxware[0]) / ".." / "lib"
        self._bin = self._lib
        if not (Path(self._bin / "wow").exists() or Path(self._bin / "wow.exe").exists()):
            self._bin = Path(self._lxware[0]) / ".." / "bin"
        self._bin = str(self._bin.resolve())
        self._lib = str(self._lib.resolve())
        self._language_info = None
        self._data = {}

    @property
    @check_language_info
    def language_info(self) -> dict[str, dict]:
        return self._language_info

    @property
    def data(self) -> dict:
        return self._data

    @property
    def bin(self) -> str:
        """:return: a (``str``) with the location of the executables (wow)"""
        return self._bin  # type: ignore

    @property
    def lib(self) -> str:
        """:return: a (``str``) with the location of the libraries (wow)"""
        return self._lib  # type: ignore

    @property
    def lxware(self) -> List[Path]:
        """:return: a (``str``) with the location of the lingware files"""
        return self._lxware

    def __str__(self) -> str:
        return f"""<{__name__} lxware={[str(fn) for fn in self.lxware]}, bin={str(self.bin)}, lib={str(self.lib)} >"""

    def purge(self, nrof_domains=None, life_time=None):
        """
        purge the domains loaded in the engine. If no arguments have been passed, then all domains will be removed.

        :param: nrof_domains: number of domains we want to keep in the cache.
        :param: life_time: The time in seconds of the domains you want to keep.
                           Remove all the domains that have not been accessed older the life_time value.
        """
        purge_info = {}
        if nrof_domains:
            purge_info["nrof_domains"] = nrof_domains
        if life_time:
            purge_info["life_time"] = life_time
        self._cpp.purge(str(purge_info))

    def release_domain(self, domain_descriptor):
        """release a specific domain"""
        self._cpp.release_domain(str(domain_descriptor))

    def info(self):
        return json.loads(self._cpp.info())

    def components(self, type: str = "", language: str = "") -> list[ComponentInfo]:
        """
        :return: a list of components that are loaded in the engine
        """
        # did not put it on top so not to break older versions
        from wowool.common.utilities import split_component

        components = []
        unique_components = set()
        if type == "language" or type == "":
            for lxware_path in self.lxware:
                for dm_fn in lxware_path.glob(f"**/{language}*.language"):
                    unique_components.add(dm_fn)

            for la_fn in unique_components:
                if lang_info := split_component(la_fn.name):
                    la = json.loads(la_fn.read_text())
                    if "short_description" in la:
                        lang_info["description"] = la["short_description"]
                    components.append(ComponentInfo(**lang_info))

        unique_domains = set()
        if type == "domain" or type == "":
            for lxware_path in self.lxware:
                for dm_fn in lxware_path.glob(f"**/{language}*.dom"):
                    unique_domains.add(dm_fn)
            for dm_fn in unique_domains:
                # domain = {"name": dm_fn.stem, "type": "domain"}
                if domain := split_component(dm_fn.name):
                    domain["type"] = "domain"
                    dm_info_fn = dm_fn.with_suffix(".dom_info")
                    if dm_info_fn.exists():
                        dm_info = json.loads(dm_info_fn.read_text())
                        if "short_description" in dm_info:
                            domain["description"] = dm_info["short_description"]
                    components.append(ComponentInfo(**domain))

        if (type == "app" or type == "") and language == "":
            from wowool.apps.info import info as apps_info

            for app_id, app_info in apps_info.items():
                app = {"name": app_id, "type": "app"}
                if "short_description" in app_info:
                    app["description"] = app_info["short_description"]

                components.append(ComponentInfo(**app, version="latest"))
        return components


if "WOWOOL_ROOT" in os.environ:
    wowool_root = Path(os.environ["WOWOOL_ROOT"]).resolve()
    default_lxware = os.environ["WOWOOL_ROOT"]
else:
    THIS_DIR = Path(__file__).parent.resolve()
    wowool_root = THIS_DIR / ".." / "package"

default_lxware = wowool_root / "lxware"


_engine = None


def default_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = Engine(language="auto", pytryoshka="true", root_path=str(wowool_root))
    return _engine


def release_engine():
    global _engine
    _engine = None


class Component:
    def __init__(self, engine: Union[Engine, None] = None):
        if engine is None:
            self._engine = default_engine()
        else:
            assert isinstance(
                engine, Engine
            ), f"engine argument is not of the type, wowool.native.core.engine.Engine but is of the type {type(engine)}"
            self._engine = engine

    @property
    def engine(self) -> Engine:
        return self._engine


@atexit.register
def _cleanup():
    release_engine()
