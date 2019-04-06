from lets import module

def do(path:str, data:bytes, options:dict=None) -> bytes:
    """
    Build and execute a module with the specified data
    and options.

    :param path: Path to module
    :param data: Data to be used by module, in bytes
    :param options: Dict of options to be used by module
    :return: Results of module execution, in bytes
    """
    mod = module.Module.build(path)
    if mod:
        gen = mod.do(data, options)
        if gen:
            return b"".join(gen)
    return b""