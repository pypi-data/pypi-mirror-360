import wowool.package.lib.wowool_sdk as cpp


def is_valid_version_format(version: str):
    """check if the version number is either a digit format separated by dots max 3 or latest or dev."""
    return cpp.is_valid_version_format(version)
