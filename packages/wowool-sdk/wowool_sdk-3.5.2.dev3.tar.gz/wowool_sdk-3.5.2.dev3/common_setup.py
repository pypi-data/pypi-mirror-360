from pathlib import Path
import os
import shutil


def copy_with_lnk(src, dst):
    dst = Path(dst)
    src = Path(src)

    if os.path.islink(src):
        linkto = os.readlink(src)

        # Remove existing destination if it exists
        if os.path.lexists(dst):
            os.unlink(dst)

        try:
            # Try to determine if the link is relative or absolute
            target_path = Path(linkto)
            if not target_path.is_absolute():
                # If relative, maintain the same relative path
                dst.parent.mkdir(parents=True, exist_ok=True)
                dir_fd = os.open(dst.parent, os.O_RDONLY)
                os.symlink(linkto, dst, dir_fd=dir_fd)
                os.close(dir_fd)
                if not os.path.islink(dst):
                    raise RuntimeError(f"Failed to create symlink {dst} -> {linkto}")

            else:
                # If absolute, we need to determine the new absolute path
                # or just copy the file directly as a fallback

                target_file = src.parent / linkto if not os.path.isabs(linkto) else Path(linkto)
                if target_file.exists():
                    # Just copy the target file directly instead of creating a symlink
                    shutil.copy2(target_file, dst)
                else:
                    # Create a symlink anyway, might work in some environments
                    os.symlink(linkto, dst)

        except Exception as ex:
            print(f"Error creating symlink: {ex}")
            raise ex
    else:
        # Regular file copy
        shutil.copy2(src, dst)


def copy_to_package_folder(site_packages: Path, wow_sdk_folder: Path, bin_folders: Path, inc_folders: Path, lib_folders: Path):
    """
    Copy the files to the package folder
    """
    print(f"[WOW]  site_packages: {site_packages=}")
    try:
        wowool_package_lib = site_packages / "wowool" / "package" / "lib"
        print(f"[WOW]  wowool_package_lib: {wowool_package_lib=}")
        wowool_package_lib.mkdir(parents=True, exist_ok=True)

        for fn in bin_folders.glob("*"):
            print(f"[WOW]  bin: {fn.name}")
            copy_with_lnk(fn, wowool_package_lib / fn.name)

        for fn in lib_folders.glob("*"):
            copy_with_lnk(fn, wowool_package_lib / fn.name)

        print(f"[WOW]  Folders : WOWOOL_STAGE: {wow_sdk_folder=} {inc_folders=} {lib_folders=}")
        if lib_folders.exists() and inc_folders.exists():
            os.environ["WOWOOL_STAGE"] = str(wow_sdk_folder)
            # WOWOOL_STAGE = wow_sdk_folder
            print("wowool.package folder:", wowool_package_lib)
        else:
            print(
                """[WOWOOL] You will need to set the WOWOOL_STAGE folder, to build the native package.
This should be in your environment ..../wowool/package"""
            )
            exit(-1)
    except Exception as ex:
        print(f"""[WOWOOL] {ex} Could not copy tile to stage folder""")
        raise ex
