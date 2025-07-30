def main():

    import subprocess
    import sys
    from pathlib import Path
    import platform

    ext = ".exe" if "Windows" == platform.system() else ""
    cpp_app = Path(__file__).parent.parent / "package" / "lib" / f"woc++{ext}"
    sys.argv[0] = str(cpp_app)
    subprocess.run(sys.argv, check=True)


if __name__ == "__main__":
    main()
