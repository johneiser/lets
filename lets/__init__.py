
def do(path:str, data:bytes, options:dict=None) -> bytes:
    """
    Build and execute a module with the specified data
    and options.

    :param path: Path to module
    :param data: Data to be used by module, in bytes
    :param options: Dict of options to be used by module
    :return: Results of module execution, in bytes
    """
    mod = Module.build(path)
    if mod:
        return b"".join(mod.do(data, options))
    return b""