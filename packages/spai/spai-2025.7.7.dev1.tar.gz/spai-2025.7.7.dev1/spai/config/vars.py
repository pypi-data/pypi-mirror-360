import json
import os
from typing import Dict


class SPAIVars:
    def __init__(self):
        current_dir = os.getcwd()
        max_tries, current_try = 3, 1
        self.vars = None
        while current_try <= max_tries:
            file_path = current_dir + "/spai.vars.json"
            if os.path.isfile(file_path):
                print(f"Loading vars from {file_path}")
                with open(current_dir + "/spai.vars.json") as f:
                    self.vars = json.load(f)
                break
            current_try += 1
            # go up one directory
            current_dir = os.path.dirname(current_dir)
        if self.vars is None:
            print("No vars file found")

    def __getitem__(self, key):
        if self.vars and key in self.vars:
            return self.vars[key]
        else:
            raise KeyError(f"{key} not found in vars")
        
    def __setitem__(self, key, value):
        if self.vars:
            self.vars[key] = value
        else:
            raise KeyError(f"No vars found")

    def __repr__(self) -> str:
        if self.vars:
            return json.dumps(self.vars, indent=2)


def parse_vars(vars) -> Dict:
    variables = {}
    for var in vars:
        key, value = var.split("=")
        try:
            # Attempt to parse the value as JSON
            value = json.loads(value)
        except json.JSONDecodeError:
            # If it's not valid JSON, leave it as a string
            pass
        variables[key] = value
    return variables
