from lets import module


def do(path:str, data:bytes=None, options:dict=None, generate:bool=False) -> bytes:
    """
    Build and execute a module with the specified data
    and options.

    :param path: Path to module
    :param data: Data to be used by module, in bytes
    :param options: Dict of options to be used by module
    :param generate: Choose to return a generator or bytes
    :return: Results of module execution, in bytes
    """
    mod = module.Module.build(path)
    if mod:
        gen = mod.do(data, options)
        if gen:
            return gen if generate else b"".join(gen)
    return iter(()) if generate else b""

def help(path:str) -> str:
    """
    Produce a help statement for the specified module.

    :param path: Path to module
    :return: Formatted help statement
    """
    mod = module.Module.build(path)
    if mod:
        parser = mod.usage()
        return parser.format_help()
    return None

def list() -> list:
    """
    Produce a list of available modules.

    :return: List of available modules
    """
    return [mod.replace(".", "/") for mod in module.Module.identify_all()]

def exists(path:str) -> str:
    """
    Check if the specified module exists.

    :param path: Path to module
    :return: True of module exists
    """
    try:
        mod = module.Module.build(path)
        return mod is not None
    except module.Module.Exception as e:
        pass
    return False