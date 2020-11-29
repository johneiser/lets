from lets.__module__ import Module, iter_module_paths


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
            for path in iter_module_paths():
                yield path.encode()
