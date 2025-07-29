import argparse

import os

original_cwd = os.getcwd()
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

from . import generate
from . import run_model
from . import download_setup
from . import delete_model
from .json_utils import write_json

write_json("og_cwd",original_cwd)

def main():
    parser = argparse.ArgumentParser(
        prog = "ezcmt",
        description = "ezcmt"
    )

    subparsers = parser.add_subparsers(
        title = "Available commands",
        dest = "command"
    )

    generate.add_subparser(subparsers)
    run_model.add_subparser(subparsers)
    download_setup.add_subparser(subparsers)
    delete_model.add_subparser(subparsers)

    args = parser.parse_args()

    if hasattr(args,"func"):
        args.func(args)
    else:
        parser.print_help()