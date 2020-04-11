import unittest, os
from lets.module import Module, BASE_DIRS
from lets.logger import log

class Bash(Module):
    """
    Generate auto-completion material for bash.
    """

    @classmethod
    def add_arguments(cls, parser):
        parser.suppress_argument("iterate")
        parser.add_argument("-l", "--list", action="store_true", help="list module directories")

    def do(self, list, **kwargs):
        if self.has_input():
            log.debug("Ignoring supplied input data")

        if list is True:
            for base in BASE_DIRS:
                data = os.path.join(base, "modules")
                yield data.encode("ascii")

        else:
            yield """
# lets bash completion start
_lets()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    if [[ ${prev} == "lets" ]] ; then
        base=($(lets complete/bash --list --generate))
        opts='$(for i in "${base[@]}";do find $i -type f -name "*.py"  2>/dev/null | sed -e "s|^$i/*||" -e "s|.py$||"; done)'    
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -o default -F _lets lets
# lets bash completion end
""".encode("ascii")