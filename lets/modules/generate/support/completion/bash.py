from lets.module import Module
from lets.utility import Utility
from lets.extensions.docker import DockerExtension

import os


class Bash(DockerExtension, Module):
    """
    Generate a bash autocomplete stub for the lets framework.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Allow for manual specification of the modules directory
        parser.add_argument("-m", "--modules",
            help="specify modules directory (default=auto)",
            type=str,
            default=None)

        return parser

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution,
            in bytes
        """
        super().do(data, options)

        # Get module directory
        if not self.options.get("modules"):
            self.options["modules"] = os.path.abspath(os.path.sep.join([Utility.core_directory(), "modules"]))

        # Build autocomplete
        autocomplete = """
# lets bash completion start
# _modules="$(python3 -c 'from lets.utility import Utility;print(Utility.core_directory())')/modules"
_modules="%(modules)s"
_lets()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts='$(find "$_modules" -type f -name "*.py" | sed -e "s|^$_modules/*||" -e "s|.py$||")'
    if [[ ${prev} == "lets" ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -o default -F _lets lets
# lets bash completion end
""" % self.options

        yield autocomplete.encode()

    @DockerExtension.ImageDecorator(["python:3"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """

        # Test directory
        modules = os.path.abspath(os.path.sep.join([Utility.core_directory(), "modules"]))
        self.assertTrue(
            os.path.exists(modules),
            "Invalid modules directory")

        # Test script generation
        modules_mount = "/tmp/modules"
        script = b"".join(self.do(options={"modules" : modules_mount}))
        self.assertTrue(
            len(script) > 0,
            "Generated empty script")

        # Test execution
        script_mount = "/tmp/script"
        cmd = "source %s" % script_mount

        # Mount script
        with self.IO(script, infile=script_mount) as io:

            # Mount volumes
            io.volumes[modules] = {
                "bind" : modules_mount,
                "mode" : "ro",
            }

            # Build docker container
            with self.Container(
                image="python:3",
                network_disabled=True,
                volumes=io.volumes,
                entrypoint=["bash", "-c"],
                command=[cmd]) as container:

                # Fetch output
                output = [line.strip() for line in container.logs(stdout=True, stderr=True)]

                # Wait for container to cleanup
                container.wait()

                # Verify execution was successful
                self.assertFalse(output, "Execution produced an error: %s" % output)