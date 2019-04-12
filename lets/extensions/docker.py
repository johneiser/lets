import os, sys, argparse, pprint, docker, logging, tempfile, subprocess

from lets.extension import Extension
from lets.logger import Logger
from lets.utility import Utility

class DockerExtension(Extension, object):
    """
    Extend a module with specific utilities for handling
    docker instances.
    """

    images = []
    """
    A list of docker images required by the module.
    """

    @property
    def client(self) -> object:
        """
        Provide a common connection to the docker daemon.

        :return: Docker client object
        """
        if not (hasattr(self, "_client") and self._client):
            self._client = docker.from_env()
        return self._client

    class IO(object):
        """
        Context manager for using input/output files with a docker container.
        """

        def __init__(self, data:bytes=None, infile:str="/data/in", outfile:str="/data/out"):
            """
            Create input and output files.

            :param data: Data to include in infile
            :param infile: Name of infile inside docker container
            :param outfile: Name of outfile inside docker container
            """
            self.volumes = {}
            self.infile = None
            self.outfile = None

            # Configure input file
            if data:
                self.infile = tempfile.NamedTemporaryFile(dir="/tmp")
                self.infile.write(data)
                self.infile.seek(0)
                self.volumes[self.infile.name] = {
                    "bind" : infile,
                    "mode" : "ro"
                }

            # Configure output file
            self.outfile = tempfile.NamedTemporaryFile(dir="/tmp")
            self.volumes[self.outfile.name] = {
                "bind" : outfile,
                "mode" : "rw"
            }

        def __enter__(self):
            """
            Open io context.
            """
            return self

        def __exit__(self, etype, value, traceback):
            """
            Close io context and clean up temporary files.
            """

    class Container(Logger, object):
        """
        Context manager for using a docker container.
        """
        def __init__(self, **kwargs):
            """
            Create an ephemeral docker container.
            """

            # Ensure some necessary options are set
            kwargs.update({

                # Ephemeral
                "auto_remove" : True,

                # Asynchronous
                "detach" : True

                })

            try:
                client = docker.from_env()
                self.container = client.containers.run(**kwargs)
                self.info("Running in new %s docker container: %s" % (kwargs.get("image"), self.container.name))

            except docker.errors.APIError as e:
                self.throw(e)

        def __enter__(self):
            """
            Open container context.
            """
            return self

        def __exit__(self, etype, value, traceback):
            """
            Close container context and clean up container.
            """
            try:
                if self.container:
                    self.container.kill()
            except docker.errors.APIError as e:
                pass

        def logs(self, **kwargs):
            """
            Return a generator of the container logs.

            :param stdout: Choose to include stdout
            :param stderr: Choose to include stderr
            """

            # Ensure some necessary options are set
            kwargs.update({

                # Generator
                "stream" : True,

                # Live
                "follow" : True

                })

            try:
                return self.container.logs(**kwargs)
            except Exception as e:
                raise(e)

        def wait(self):
            """
            Wait for container to finish.
            """
            self.container.wait()

        def interact(self):
            """
            Open a TTY to interact with the container.
            """
            proc = subprocess.Popen("docker attach %s" % self.container.name,
                shell=True,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr)
            proc.communicate()

    def _prep(self):
        """
        Prepare all required docker images.
        """
        for tag in self.images:
            image = None

            # Check if image already exists
            try:
                self.info("Checking for existing docker image: %s" % tag)
                image = self.client.images.get(tag)
            except docker.errors.ImageNotFound as e:
                pass
            except docker.errors.APIError as e:
                self.throw(e)

            if image is None:
                # Check if image can be build locally
                try:
                    self.info("Trying to build docker image: %s" % tag)
                    [name,_,version] = tag.partition(":")
                    path = os.path.sep.join([Utility.core_directory(), "images", name])
                    image, logs = self.client.images.build(
                        tag=tag,
                        path=path,
                        pull=True)
                except docker.errors.BuildError as e:
                    self.throw(e)
                except docker.errors.APIError as e:
                    self.throw(e)
                except TypeError as e:
                    pass

            if image is None:
                # Check if image can be pulled remotely
                try:
                    self.info("Trying to pull docker image: %s" % tag)
                    image = self.client.images.pull(tag)
                except docker.errors.ImageNotFound as e:
                    pass
                except docker.errors.APIError as e:
                    self.throw(e)

            if image is None:
                # No more options, throw exception
                self.throw(Exception("Missing required docker image: %s" % tag))

            else:
                self.info("Acquired docker image: %s" % tag)

    def usage(self) -> object:
        parser = super().usage()

        return parser
    
    def do(self, data:bytes=None, options:dict=None) -> bytes:
        super().do(data, options)

        self._prep()

        return iter(())

    def setUp(self):
        super().setUp()
        self._prep()

    def tearDown(self):
        super().tearDown()