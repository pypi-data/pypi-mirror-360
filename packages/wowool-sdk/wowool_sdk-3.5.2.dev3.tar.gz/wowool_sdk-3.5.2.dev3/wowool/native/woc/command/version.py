from wowool.io.console import console
from wowool.native.core.engine import default_engine


def command(**kwargs):
    info = default_engine().info()
    if "sdk_version" in info:
        console.print(info["sdk_version"])
    else:
        console.print("could not find version info")
    # console.print(f"version = {__version__}")
    return 0
