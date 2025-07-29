import argparse
import gdown
import shutil
import os
import subprocess
from .json_utils import write_json,read_json
import sys

write_json("ollama_installed",shutil.which("ollama") == True)

def add_subparser(subparsers):
    setup = subparsers.add_parser(
        "setup",
        help = "Setup ezcmt."
    )

    setup.set_defaults(func=setup_func)

def setup_func(args):
    model_downloaded = read_json("model_downloaded")

    if model_downloaded:
        print("The model is already downloaded.")
    else:
        model_folder = "cli_tool/ezcmt-model"
        try:
            os.mkdir(model_folder)
        except Exception:
            pass

        try:
            gdown.download("https://drive.google.com/uc?id=1o4hX3fzGAuAE-d3G-nx0N8GQbLZ09AZU",
                        model_folder + "/Modelfile")
        except Exception:
            print("Modelfile already exists. It could be because you didnt delete the model files before uninstalling ezcmt. Run 'ezcmt delete-model' before uninstalling ezcmt to remove the model files.")

        try:
            gdown.download("https://drive.google.com/uc?id=1aV-TM360UCtj2Fgu9QAQKvUF80ZlWGkU",
                            model_folder + "/ezcmt-q8_0.gguf")
        except Exception:
            print("LoRA's file already exists. It could be because you didnt delete the model files before uninstalling ezcmt. Run 'ezcmt delete-model' before uninstalling ezcmt to remove the model files.")

        try:
            gdown.download("https://drive.google.com/uc?id=1_Ob-YzYzpUKf9TvN1heeQTHkVBnPuC-S",
                            model_folder + "/Mistral-7B-v0.3.Q8_0.gguf")
        except Exception:
            print("Base model's file already exists. It could be because you didnt delete the model files before uninstalling ezcmt. Run 'ezcmt delete-model' before uninstalling ezcmt to remove the model files.")

        print("The model is downloaded.")

        write_json("model_downloaded",True)
    
    if read_json("ollama_installed"):
        print("Ollama is already installed.")
    
    else:
        if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
            gdown.download("https://drive.google.com/uc?id=1er8wPF-LTETLzsp09KA51fl8V0RisdAD",
                            r"cli_tool\OllamaSetup.exe")
            
            print("Launched Ollama setup, check the background apps to find it.")
            subprocess.run(r"cli_tool\OllamaSetup.exe")

        elif sys.platform.startswith("linux"):
            os.system("curl -fsSL https://ollama.com/install.sh | sh")
        
        else:
            
            if shutil.which("brew") == None:
                os.system("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")    
                subprocess.run(f"echo 'eval \"$(/opt/homebrew/bin/brew shellenv)\"' >> /Users/{os.getlogin()}/.zprofile",shell=True,executable="/bin/bash")
                subprocess.run("eval \"$(/opt/homebrew/bin/brew shellenv)\"",shell=True,executable="/bin/bash")
            
            os.system("brew install --cask ollama")
        
        print("Ollama is installed.")
        write_json("ollama_installed",True)

    if read_json("setup_done") == False:
        
        subprocess.run(["ollama","create","-f","cli_tool/ezcmt-model/Modelfile","_ezcmt"])

        print("Setup done.")
        write_json("setup_done",True)
    
    else:
        print("Setup is already done.")