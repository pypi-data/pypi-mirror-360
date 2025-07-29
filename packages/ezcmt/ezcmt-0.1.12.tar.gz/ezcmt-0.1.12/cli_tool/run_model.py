import subprocess
import sys
import os
import signal
import argparse
from .json_utils import write_json,read_json

def add_subparser(subparsers):
    run_parser = subparsers.add_parser(
        "run-model",
        help = "Make the model run in the background to get faster generation."
    )

    run_parser.set_defaults(func = run)

def run(args):
    if sys.platform == "win32":
        proc = subprocess.Popen(["cmd.exe","/k","ollama","run","_ezcmt"],
                            creationflags = subprocess.CREATE_NO_WINDOW)
    else:
        try:
            script = f"""
tell application "Terminal"
    activate
    do script "zsh -c 'ollama run _ezcmt; exec zsh'"
    set miniaturized of front window to true
end tell
"""
            proc = subprocess.Popen(["osascript","-e",script],stdout=subprocess.DEVNULL)
            print("The model is running and the terminal is minimized.")
        except Exception:
            try:
                proc = subprocess.Popen("gnome-terminal","--","zsh","-c","ollama run _ezcmt; exec zsh")
            except Exception:
                proc = subprocess.Popen("xterm","-e",'zsh -c "ollama run _ezcmt; exec zsh"')