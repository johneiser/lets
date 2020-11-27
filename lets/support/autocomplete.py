from lets.__module__ import Module
import os, pkg_resources

class Autocomplete(Module):
    """
    Generate auto-completion material.
    """

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("platform", nargs="?", choices=["bash"])

    def handle(self, input, platform=None): 
        
        # Generate autocomplete script for given platform
        if platform:
            if platform == "bash":
                yield """
# lets bash completion start
_lets()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    if [[ ${prev} == "lets" ]] ; then
        base=($(lets support/autocomplete -g))
        opts='$(for i in "${base[@]}";do find $i -type f -name "[^_]*.py" 2>/dev/null | sed -e "s|^$i/*||" -e "s|.py$||"; done)'
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -o default -F _lets lets
# lets bash completion end
""".encode()

        # Generate list of module directories
        else:
            found = []

            # Import core and extended modules
            base,_,_ = self.__file__.partition(
                    self.__name__.replace(os.path.extsep, os.path.sep))
            core = os.path.join(base, "lets")
            yield core.encode()
            found.append(core)

            # Import auxiliary modules from other packages. To include, add
            # the following to setup.py:
            # 
            #   setup(
            #       ...
            #       entry_points = {
            #           "lets" : [ "modules=[PACKAGE NAME]:[PATH TO MODULES]" ],
            #       }
            #   )
            for entry in pkg_resources.iter_entry_points("lets"):
                if entry.name == "modules":
                    for attr in entry.attrs:
                        path = os.path.join(entry.dist.location, entry.module_name, attr)
                        if path not in found:
                            yield path.encode()
                            found.append(path)
