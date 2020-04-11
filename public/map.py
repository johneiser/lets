"""
Generate a json map of modules for use with jstree.

Usage: python3 map.py > map.json
"""
import os, json, lets

MODULE_BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lets",
    "modules"
)

def generate():
    """Generate map of modules."""
    base = MODULE_BASE

    # Walk base directory
    for root, dirs, files in os.walk(base):
        [_,_,path] = root.partition(base + os.path.sep)

        # Yield folder
        if path:
            [parent,_,folder] = path.rpartition(os.path.sep)
            yield {
                "id" : path,
                "parent" : parent or "#",
                "text" : folder,
            }

        # Yield modules
        for file in files:
            [name,_,ext] = file.rpartition(os.path.extsep)
            module = os.path.join(path, name)
            try:
                yield  {
                    "id" : module + "_",
                    "parent" : path or "#",
                    "text" : name,
                    "type" : "module",
                    "help" : lets.help(module),
                }
            except ModuleNotFoundError as e:
                pass

def main():
    """Output map of modules."""
    print(json.dumps(list(generate())))

if __name__ == "__main__":
    main()