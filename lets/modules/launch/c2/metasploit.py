from lets.module import Module
from lets.extensions.docker import DockerExtension

import os


class Metasploit(DockerExtension, Module):
    """
    Launch a `Metasploit`_ console and its associated postgres database. The
    database listens on localhost:5432/tcp by default with credentials
    msf/msf, but can be customized.

    .. _Metasploit:
        https://www.offensive-security.com/metasploit-unleashed/
    """
    interactive = True

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Share directories with container, if desired
        parser.add_argument("-d", "--directory",
            help="directory to share with container",
            type=str,
            action="append",
            dest="directories",
            default=[])

        # Configure database specifics
        parser.add_argument("--port",
            help="change postgres port (default=%(default)d)",
            type=int,
            default=5432)
        parser.add_argument("--interface",
            help="change postgres interface (default=%(default)s)",
            type=str,
            default="127.0.0.1")
        parser.add_argument("--user",
            help="change postgres user (default=%(default)s)",
            type=str,
            default="msf")
        parser.add_argument("--password",
            help="change postgres password (default=%(default)s)",
            type=str,
            default="msf")

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

        volumes = {}

        for directory in self.options.get("directories"):

            # Validate directory
            try:
                assert os.path.isdir(directory), "Invalid directory: %s" % directory
            except AssertionError as e:
                self.throw(e)

            # Mount directory in container
            directory = os.path.abspath(directory)
            volumes[directory] = {
                "bind" : directory,
                "mode" : "rw"
            }
            self.info("Mounting directory: %s" % directory)

        # Prepare database container
        with self.Container(
            image="postgres:latest",
            ports={
                "5432/tcp" : ("127.0.0.1", self.options.get("port")),
            },
            environment={
                "POSTGRES_USER" : self.options.get("user"),
                "POSTGRES_PASSWORD" : self.options.get("password"),
            }) as db:

            self.info("Started database: %(user)s:%(password)s@%(interface)s:%(port)d" % self.options)

            # Prepare Metasploit container to connect to database
            with self.Container(
                image="metasploitframework/metasploit-framework:latest",
                network_mode="host",
                stdin_open=True,
                tty=True,
                volumes=volumes,
                extra_hosts={
                    "db" : self.options.get("interface"),
                },
                environment={
                    "DATABASE_URL" : "%(user)s:%(password)s@db:%(port)d" % self.options,
                }) as container:

                # Enter container
                container.interact()

    @DockerExtension.ImageDecorator(["metasploitframework/metasploit-framework:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
