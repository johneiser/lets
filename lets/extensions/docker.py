from lets.extension import Extension
from lets.logger import Logger
from lets.utility import Utility, TEMP_DIRECTORY
import os, sys, docker, tempfile, subprocess, functools


class DockerExtension(Extension, object):
    """
    Extend a module with specific utilities for handling
    docker containers.
    """

    @property
    def client(self) -> object:
        if not (hasattr(self, "_client") and self._client):
            self._client = docker.from_env()
        return self._client

    class IO(object):
        """
        Context manager for using input/output files with a docker container.
        """

        volumes = {}
        """
        A dict representing the infile and outfile, appropriate for
        constructing a docker container.
        """

        def __init__(self, data:bytes=None,
            infile:str="/data/in", outfile:str="/data/out"):
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
                self.infile = tempfile.NamedTemporaryFile(dir=TEMP_DIRECTORY)
                self.infile.write(data)
                self.infile.seek(0)
                self.volumes[self.infile.name] = {
                    "bind" : infile,
                    "mode" : "ro"
                }

            # Configure output file
            self.outfile = tempfile.NamedTemporaryFile(dir=TEMP_DIRECTORY)
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
        Context manager to produce a docker container.
        Simply a wrapper around `Docker-Py Container.run()`_,
        kwargs can be passed in to customize the container.

        .. _Docker-Py Container.run():
            https://docker-py.readthedocs.io/en/stable/containers.html#module-docker.models.containers
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
                self.info("Running in new %s docker container: %s" %
                    (kwargs.get("image"), self.container.name))

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
            pass

        def __del__(self):
            """
            Clean up container.
            """
            try:
                if hasattr(self, "container") and self.container:
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

    class ImageDecorator(Logger):
        """
        Decorator to fetch required docker images prior to the
        execution of the function.
        """
        def __init__(self, images:list):
            """
            Initialize decorator with a list of images.

            :param: Images to fetch prior to execution
            """
            self.images = images

        def __call__(self, func, *args, **kwargs) -> object:
            """
            Build a decorated wrapper function around the original function.

            :param func: Original function
            :param *args: Original *args
            :param **kwargs: Original **kwargs
            :return: Decorated wrapper function
            """
            # Keep docustrings for original function
            @functools.wraps(func)

            # Build wrapper function
            def wrapper(*args, **kwargs):

                # Build required docker images before executing
                self.prep(self.images)
                return func(*args, **kwargs)

            return wrapper

        @property
        def client(self) -> object:
            if not (hasattr(self, "_client") and self._client):
                self._client = docker.from_env()
            return self._client

        def prep(self, images:list):
            """
            Prepare required docker images.

            :param images: List of required docker images
            """
            for tag in images:
                image = None

                # Check if image already exists
                try:
                    image = self.client.images.get(tag)
                    if image is not None:
                        # self.info("Found required docker image: %s" % tag)
                        continue

                except docker.errors.ImageNotFound as e:
                    pass
                except docker.errors.APIError as e:
                    self.throw(e)

                self.warn("Missing required docker image: %s" % tag)

                # Check if image can be built locally
                try:
                    [name,_,version] = tag.partition(":")
                    path = os.path.sep.join([Utility.core_directory(), "images", name])

                    if os.path.isdir(path):
                        # self.info("Trying to build docker image: %s" % tag)
                        proc = subprocess.Popen("docker build --rm -t %s %s" % (tag, path),
                            shell=True,
                            stdout=self._log_stream,
                            stderr=self._log_stream)
                        proc.communicate()

                    image = self.client.images.get(tag)
                    if image is not None:
                        # self.info("Built required docker image: %s" % tag)
                        continue

                except docker.errors.ImageNotFound as e:
                    pass
                except docker.errors.BuildError as e:
                    self.throw(e)
                except docker.errors.APIError as e:
                    self.throw(e)

                # Check if image can be pulled remotely
                try:
                    # self.info("Trying to pull docker image: %s" % tag)
                    proc = subprocess.Popen("docker pull %s" % (tag),
                        shell=True,
                        stdout=self._log_stream,
                        stderr=self._log_stream)
                    proc.communicate()

                    image = self.client.images.get(tag)
                    if image is not None:
                        # self.info("Pulled required docker image: %s" % tag)
                        continue

                except docker.errors.ImageNotFound as e:
                    pass
                except docker.errors.APIError as e:
                    self.throw(e)

                # No more options, throw exception
                self.throw(Exception("Unable to find required docker image: %s" % tag))
