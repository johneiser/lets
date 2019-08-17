from lets.module import Module
from lets.extensions.docker import DockerExtension

import os


class Postgres(DockerExtension, Module):
    """
    Launch a postgres database.
    """
    interactive = True

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Configure data
        parser.add_argument("-d", "--directory",
            help="use directory for database storage",
            type=str,
            default=None)

        # Configure listener
        parser.add_argument("--port",
            help="change postgres port (default=%(default)d)",
            type=int,
            default=5432)
        parser.add_argument("--interface",
            help="change postgres interface (default=%(default)s)",
            type=str,
            default="127.0.0.1")

        # Configure authentication
        parser.add_argument("--user",
            help="change postgres user (default=%(default)s)",
            type=str,
            default="postgres")
        parser.add_argument("--password",
            help="change postgres password (default=%(default)s)",
            type=str,
            default="postgres")

        return parser

    @DockerExtension.ImageDecorator(["postgres:latest"])
    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        # Configure environment
        environment = {
            "POSTGRES_USER" : self.options.get("user"),
            "POSTGRES_PASSWORD" : self.options.get("password"),
        }

        # Configure volumes
        volumes = {}

        directory = self.options.get("directory")
        if directory:

            # Validate directory
            try:
                assert os.path.isdir(directory), "Invalid directory: %s" % directory
            except AssertionError as e:
                self.throw(e)

            # Mount directory in container
            volumes[os.path.abspath(directory)] = {
                "bind" : "/var/lib/postgresql/data",
                "mode" : "rw"
            }

            # Adjust container to handle mounted directory
            environment["PGDATA"] = "/var/lib/postgresql/data/pgdata"

        # Prepare database container
        with self.Container(
            image="postgres:latest",
            ports={
                "5432/tcp" : (self.options.get("interface"), self.options.get("port")),
            },
            volumes=volumes,
            environment=environment) as container:

                # Enter container
                container.interact()

    @DockerExtension.ImageDecorator(["postgres:latest"])
    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
