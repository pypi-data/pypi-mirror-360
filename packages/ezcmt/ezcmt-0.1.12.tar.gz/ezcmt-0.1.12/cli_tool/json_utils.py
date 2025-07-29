import json

def write_json(key,value):
    with open("cli_tool/state.json","r") as r:
        try:
            state = json.load(r)
        except Exception:
            state = dict()

    state[key] = value

    with open("cli_tool/state.json","w") as w:
        json.dump(state,w,indent=4)

def read_json(key):
    with open("cli_tool/state.json","r") as r:
        return json.load(r)[key]