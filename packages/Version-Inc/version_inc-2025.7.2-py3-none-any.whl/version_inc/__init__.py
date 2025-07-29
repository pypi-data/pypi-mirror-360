import argparse
import datetime
import json
import os
import re
from pathlib import Path

from version_inc.terminal_formatting import add_color

CONFIG_FILE = "vinc.json"
VARIABLES = ["YEAR", "MONTH", "DAY", "COUNTER", "MAJOR", "MINOR"]
DATE_VARIABLES = frozenset({"YEAR", "MONTH", "DAY"})
ANY_VARIABLE_RE = re.compile(f"<(?:{'|'.join(VARIABLES)})>")


def kw_transformation(kw):
    return f"<{kw}>"


def update_variable(name, old_value):
    match name:
        case "YEAR":
            return datetime.date.today().year
        case "MONTH":
            return datetime.date.today().month
        case "DAY":
            return datetime.date.today().day
        case "COUNTER":
            return old_value + 1
        case "MAJOR" | "MINOR":
            return old_value
    return None


def extract_var_names(template):
    output = []
    for name in VARIABLES:
        if kw_transformation(name) in template:
            output.append(name)
    return output


def replace_range(string, start, end, value):
    return string[:start] + value + string[end:]


class Target:
    def __init__(self, state, file, data):
        self.path = Path(file)
        self.find = data["find"]
        self.replace = data["replace"]
        self.state = state

    def execute(self):
        print(f"Executing target {self.path}")
        raw_find = self.find_regex()
        find = re.compile(raw_find, flags=re.DOTALL | re.IGNORECASE)
        print(f"Using regex {raw_find} to look for version strings")
        string = self.path.expanduser().read_text()
        matches = list(find.finditer(string))

        print(f"{add_color(2,len(matches))} match(es) were found in {add_color(2,self.path)}")
        replacement = self.replace
        replacement = replacement.replace("<VERSION>", str(self.state))

        print(f"Replacing matches with {replacement}")

        for match in reversed(matches):
            string = replace_range(string, match.start(), match.end(), replacement)

        self.path.expanduser().write_text(string)

    def find_regex(self):
        return self.find.replace("<VERSION>", self.state.version_re())

    def to_json(self):
        data = {
            "find": self.find,
            "replace": self.replace
        }
        return str(self.path), data


class VincState:
    def __init__(self, data):
        self.template = data["template"]
        self.variables = {}
        for name in extract_var_names(self.template):
            self.variables[name] = None
        for name in VARIABLES:
            if name in data:
                self.variables[name] = data[name]

        self.targets = []
        if "targets" in data:
            for file, value in data["targets"].items():
                self.targets.append(Target(self, file, value))

    def __str__(self):
        template: str = self.template
        for key, value in self.variables.items():
            template = template.replace(kw_transformation(key), str(value))
        return template

    def inc(self):
        changed = set()

        for name in self.variables:
            old_value = self.variables[name]
            if old_value is None:
                old_value = 0
            old_value = int(old_value)
            new_value = update_variable(name, old_value)
            if old_value != new_value:
                changed.add(name)
            self.variables[name] = new_value

        if "COUNTER" in self.variables and len(changed & DATE_VARIABLES) > 0:
            self.variables["COUNTER"] = 1

    def to_json(self):
        json_data = {
            "template": self.template,
            "version": str(self)
        }
        for key, value in self.variables.items():
            json_data[key] = value

        targets = {}
        for target in self.targets:
            file, data = target.to_json()
            targets[file] = data
        json_data["targets"] = targets
        return json_data

    def version_re(self):
        regex = self.template
        regex = re.escape(regex)
        regex = ANY_VARIABLE_RE.sub("[0-9]+", regex)
        return regex


def command_entry_point():
    try:
        run_version_inc()
    except KeyboardInterrupt:
        pass


def run_version_inc():
    parser = argparse.ArgumentParser(
        prog="Version-Inc",
        description="A lightweight tool for incrementing version numbers in files"
    )
    parser.add_argument("-ge","--generate-example",action="store_true", help=f"Generate an example {CONFIG_FILE}")
    parser.add_argument("-c","--current", action="store_true", help="Prints the current version and exits")
    args = parser.parse_args()

    path = Path(CONFIG_FILE)

    if args.generate_example:
        if path.exists():
            print(f"{CONFIG_FILE} already exists in {Path(os.curdir).resolve()}")
            print("Delete the file to allow for automatic generation of new file")
            return

        path.write_text(json.dumps({
            "template": "<MAJOR>.<MINOR>.<COUNTER>",
            "targets": {}
        },indent="\t"))

        return

    if not path.exists():
        print(f"No {CONFIG_FILE} found in current directory: {Path(os.curdir).resolve()}")
        print(f"Use vinc -ge to generate an example {CONFIG_FILE}")
        return

    with path.open() as file:
        data = json.load(file)

    state = VincState(data)

    if args.current:
        print(str(state))
        return

    print(f"The current version is {str(state)}")
    state.inc()
    print(f"The new version is {add_color(1,str(state))}")

    for target in state.targets:
        target.execute()

    path.write_text(json.dumps(state.to_json(), indent="\t"))
