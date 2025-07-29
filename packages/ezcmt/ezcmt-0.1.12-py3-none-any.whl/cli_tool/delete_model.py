import shutil
import argparse
import subprocess
from .json_utils import read_json,write_json

def add_subparser(subparsers):
    delete_parser = subparsers.add_parser(
        "delete-model",
        help = "Delete model files. Should be done before uninstalling ezcmt (otherwise the model files will stay) if you want a full cleanup."
    )

    delete_parser.set_defaults(func=delete)

def delete(args):
    model_downloaded = read_json("model_downloaded")
    if model_downloaded:
        setup_done = read_json("setup_done")
        if setup_done:
           subprocess.Popen(["ollama","rm","_ezcmt"])
        shutil.rmtree("cli_tool/ezcmt-model")
    else:
        print("The model cant be deleted because it isnt downloaded.")