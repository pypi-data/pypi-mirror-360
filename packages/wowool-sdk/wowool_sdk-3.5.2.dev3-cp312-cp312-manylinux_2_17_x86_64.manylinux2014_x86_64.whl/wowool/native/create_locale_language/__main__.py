import argparse
from pathlib import Path


def parse_arguments():
    """
    Parses the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--locale", required=True, help="locale to crate a language file")
    parser.add_argument("-l", "--language", required=True, help="name of the language file thaat will be created, without extenstion.")
    parser.add_argument("-n", "--namespace", help="namespace in lxware.", default="wowool")
    parser.add_argument("--lxware", help="location of the lxware folder")
    args = parser.parse_args()
    return args


def main(*argv):
    args = parse_arguments(*argv)
    lxware = args.lxware
    if lxware is None:
        from wowool.native.core.engine import default_lxware

        lxware = Path(default_lxware)
    else:
        lxware = Path(lxware)

    fn = lxware / args.namespace / f"{args.language}.language"
    if fn.exists():
        raise RuntimeError(f"{fn} already exists !")

    fn.write_text(
        f"""{{
    "sentyziser" : "icu",
    "tokenizer_locale": "{args.locale}",
    "short_description": "A language module that enriches words with root forms, part of speech and properties for {args.locale}"
}}
"""
    )
    print(f"generated: {fn}")
