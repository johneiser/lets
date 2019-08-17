from lets.module import Module
from lets.extensions.docker import DockerExtension

import os, ipaddress


class Metasploit(DockerExtension, Module):
    """
    Launch a `Metasploit`_ console. Optionally connect to a postgres
    database. Pass resource file contents as stdin, or specify commands
    to run with '-x'.

    .. _Metasploit:
        https://www.offensive-security.com/metasploit-unleashed/
    """
    interactive = True
    platforms = ["linux"] # Host networking does not work in VM based docker

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Share directories with container, if desired
        parser.add_argument("-d", "--directory",
            help="share directory with container",
            type=str,
            action="append",
            dest="directories",
            default=[])

        # Execute commands upon load
        parser.add_argument("-x", "--execute-command",
            help="execute the specified console commands (use ; for multiples)",
            type=str,
            action="append",
            dest="commands",
            default=[])

        # Optionally connect to a postgres database
        parser.add_argument("--database",
            help="connect to postgres host",
            type=str,
            default=None)
        parser.add_argument("--port",
            help="change postgres port (default=%(default)d)",
            type=int,
            default=5432)
        
        parser.add_argument("--user",
            help="change postgres user (default=%(default)s)",
            type=str,
            default="postgres")
        parser.add_argument("--password",
            help="change postgres password (default=%(default)s)",
            type=str,
            default="postgres")

        return parser

    @DockerExtension.ImageDecorator(["metasploitframework/metasploit-framework:latest"])
    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Container constants
        HOME = "/usr/share/metasploit-framework"

        # Defaults
        cmd = ["./msfconsole", "-r", "docker/msfconsole.rc"]
        hosts = {}
        environment = {}

        # Handle database
        database = self.options.get("database")
        if database:
            try:
                # Use IP address
                ip = ipaddress.ip_address(database)
                hosts["database"] = ip
                environment["DATABASE_URL"] = "%(user)s:%(password)s@database:%(port)d" % self.options

            except ValueError:
                # Use hostname
                environment["DATABASE_URL"] = "%(user)s:%(password)s@%(database)s:%(port)d" % self.options

        # Handle input as resource file
        if data:
            cmd.append("-r")
            cmd.append(os.path.join(HOME, "custom.rc"))

        # Handle commands
        for command in self.options.get("commands"):
            cmd.append("-x")
            cmd.append(command)

        # Prepare input and output files
        with self.IO(data, infile=os.path.join(HOME, "custom.rc")) as io:

            # Handle directories
            for directory in self.options.get("directories"):

                # Validate directory
                try:
                    assert os.path.isdir(directory), "Invalid directory: %s" % directory
                except AssertionError as e:
                    self.throw(e)

                # Mount directory in container
                directory = os.path.abspath(directory)
                io.volumes[directory] = {
                    "bind" : directory,
                    "mode" : "rw"
                }
                self.info("Mounting directory: %s" % directory)

            # Prepare Metasploit container
            with self.Container(
                image="metasploitframework/metasploit-framework:latest",
                network_mode="host",
                stdin_open=True,
                tty=True,
                volumes=io.volumes,
                extra_hosts=hosts,
                environment=environment,
                command=cmd) as container:

                # Enter container
                container.interact()

    @DockerExtension.ImageDecorator(["metasploitframework/metasploit-framework:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
