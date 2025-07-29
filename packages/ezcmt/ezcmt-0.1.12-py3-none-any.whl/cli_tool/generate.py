from ollama import chat
import subprocess
import argparse
from .json_utils import read_json

def add_subparser(subparsers):
    parser = subparsers.add_parser(
        "generate",
        help="Generate a commit message."
    )

    parser.add_argument(  
        "--count",
        help = "Number of commit messages to be generated. Default value is 3",
        type = int,
        default = 3
    )

    parser.set_defaults(func = create_msg)

def create_msg(args):
    if read_json("setup_done"):
        try:    
            patch = subprocess.run(["git","diff","--cached"],capture_output=True,
                                text=True,cwd=read_json("og_cwd"),check=True).stdout
            
            if patch:
                patch = "\n".join([line for line in patch.splitlines() if not line.startswith("index")])

                for i in range(args.count):
                    print(chat(model="_ezcmt",messages=[{"role":"user","content":patch}]).message.content)
            
            else:
                print("The current directory is not a repository or theres nothing to commit.")
        
        except Exception:
            print("Git is not installed.")
    
    else:
        print("Cant generate a commit message when setup is not done.")    