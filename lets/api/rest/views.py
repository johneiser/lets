from django.http import HttpResponse, Http404
from django.utils.http import limited_parse_qsl

# Find lets
from api.settings import BASE_DIR
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(BASE_DIR)))

from lets.module import Module

def _do(path:str, data:bytes=None, options:dict=None) -> bytes:
    """
    Build and execute a module with the specified data
    and options.

    :param path: Path to module
    :param data: Data to be used by module, in bytes
    :param options: Dict of options to be used by module
    :return: Results of module execution, in bytes
    :raises: Http404 if module not valid
    """
    try:
        mod = Module.build(path)
        if mod:
            if mod.interactive:
                raise Http404("Interactive module, not valid for API")
            gen = mod.do(data, options)
            if gen:
                return b"".join(gen)
    except Module.Exception as e:
        raise Http404(str(e))
    raise Http404("Invalid module")

def do(request, module):
    """
    Build and execute a module according to the specified request.

    :param request: Web request submitted
    :param module: Module specified, in path
    :return: Results of module execution, in bytes
    """
    return HttpResponse(_do(
        module,
        request.body,
        dict(limited_parse_qsl(request.META["QUERY_STRING"]))
        ))