import os, sys, argparse, pprint, docker, logging
from lets.module import Module
from lets.utility import Utility
from lets.logger import Logger

class DockerModule(Module):
    """
    Abstract module class specific to Docker implementations.  Provides
    specific utilities for handling docker instances.
    """

    # A list of docker images required by the module.
    images = []

    @property
    def client(self) -> object:
        """
        Provide a common connection to the docker daemon.

        :return: Docker client object
        """
        if not (hasattr(self, "_client") and self._client):
            self._client = docker.from_env()
        return self._client

    def prep(self):
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

    class Container(Logger):
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


    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        return parser
    
    def do(self, data:bytes, options:dict=None) -> bytes:
        """
        Main functionality.  Make sure any required docker containers
        are created, updated, and available.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution, in bytes
        """
        super().do(data, options)

        self.info("Docker images required: %s" % pprint.pformat(self.images))
        self.prep()

        return iter(())

    def setUp(self):
        """
        Make any necessary preparations for test.
        """
        super().setUp()
        self.prep()

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        self.fail("Not implemented")

    def tearDown(self):
        """
        Clean up after tests have run.
        """
        super().tearDown()
