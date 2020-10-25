import os, sys, argparse, logging, types, docker, tempfile, platform, subprocess, io

log = logging.getLogger(__package__)
client = docker.from_env()


class ModuleMeta(type):

    def __init__(cls, name, bases, namespace):
        super(ModuleMeta, cls).__init__(name, bases, namespace)

        # Load module as callable
        if cls.__module__ != __name__:
            sys.modules[cls.__module__].__class__ = cls


class ModuleLogger(logging.LoggerAdapter):

    def process(self, msg, kwargs):

        # Add module context to logging
        return "[%(module)s] " % self.extra + str(msg), kwargs


class Module(types.ModuleType, metaclass=ModuleMeta):
    """
    Functionality can be added to the framework by implementing
    a :py:class:`Module <lets.__module__.Module>` and strategically
    placing it in a file under the appropriate directory.

    For example, a :py:class:`Module <lets.__module__.Module>`
    placed in the file :code:`lets/encode/base64.py` will be
    accessible as :code:`lets encode/base64`.
    """
    images = []
    """
    Specify required docker images.

    .. code-block:: python

        class MyModule(Module):
            images = ["python:2.7"]
    """

    @property
    def log(self):
        """
        Display information to the user. Refer to the `logging <https://docs.python.org/3/library/logging.html>`_ documentation for guidance.

        .. code-block:: python
            
            def handle(input, **kwargs):
                self.log.info("Starting...")
                ...
                self.log.error("Failed!")
        """
        if not hasattr(self, "_log") or not self._log:
            self._log = ModuleLogger(log, {"module": self.__module__})
        return self._log

    @classmethod
    def help(cls):
        """
        Produce the help text for this module.

        :return: help text
        :rtype: str
        :meta private:
        """
        module = cls.__module__.replace(os.path.extsep, os.path.sep)
        parser = argparse.ArgumentParser("[INPUT] | " + module, description=cls.__doc__)
        parser.add_argument("-i", "--iterate", action="store_true", help="iterate over input")
        parser.add_argument("-g", "--generate", action="store_true", help="generate each output")
        parser.add_argument(      "--input", type=argparse.FileType("rb"), help=argparse.SUPPRESS)
        parser.add_argument("-o", "--output", type=argparse.FileType("wb"), help="output to file")
        parser.add_argument("-v", "--verbose", action="store_true", help="print debug info")
        cls.add_arguments(parser)
        return parser.format_help()
    
    @classmethod
    def add_arguments(cls, parser):
        """
        Customize an argument parser defining the usage of the module. Refer to the `argparse <https://docs.python.org/3/library/argparse.html>`_ documentation for guidance.

        :param ArgumentParser parser: argument parser to customize

        .. code-block:: python

            @classmethod
            def add_arguments(cls, parser):
                parser.add_argument("-f", "--flag", action="store_true")

        """

    def handle(self, input, **kwargs):
        """
        Perform the primary functionality of the module, and :code:`yield` any output.

        :param iterable input: Input provided to the module
        :param ** kwargs: Any arguments specified in :py:meth:`add_arguments <lets.__module__.Module.add_arguments>`
        :return: output
        :rtype: generator(bytes)

        .. code-block:: python

            def handle(self, input):
                for data in input:
                    yield b"(" + data + b") seen"
        """
        raise NotImplementedError(self.__module__)

    def _prep(self, images=None):
        """
        Prepare any required docker images.

        :param list images: List of required docker images to prepare
        :meta private:
        """
        # Confirm docker is installed
        if images:
            try:
                client.ping()
            except docker.errors.APIError as e:
                raise AssertionError("Unable to connect to docker, is it installed?")
        
        for tag in images or self.images:
            image = None

            # Check if image already exists
            try:
                image = client.images.get(tag)
                if image is not None:
                    self.log.debug("Found required docker image: %s", image)
                    continue
            except docker.errors.ImageNotFound as e:
                pass
            except docker.errors.APIError as e:
                self.log.warn(e)

            # Check if image can be built locally
            try:
                name,_,version = tag.partition(":")
                base,_,_ = self.__file__.partition(self.__name__.replace(os.path.extsep, os.path.sep))
                path = os.path.join(base, "lets", "__images__", name)
                if os.path.isdir(path):
                    self.log.info("Building image: %s", path)
                    client.images.build(tag=tag, path=path, pull=True)
                    image = client.images.get(tag)
                if image is not None:
                    self.log.debug("Built required docker image: %s", image)
                    continue
            except docker.errors.BuildError as e:
                self.log.warn(e)
            except docker.errors.ImageNotFound as e:
                self.log.debug(e)

            # Check if image can be pulled remotely
            try:
                self.log.info("Pulling image: %s", tag)
                image = client.images.pull(tag)
                if image is not None:
                    self.log.debug("Pulled required docker image: %s", image)
                    continue
            except docker.errors.ImageNotFound as e:
                self.log.debug(e)
            except docker.errors.APIError as e:
                self.log.error(e)

            assert image is not None, "Missing required docker image: %s" % tag

    def __call__(self, input=None, iterate=False, generate=False, **kwargs):
        """        
        Handle a call to the module and mediate components to normalize the
        module interface.

        :param object input: Input provided to the module
        :param bool iterate: Whether to iterate the input
        :param bool generate: Whether to generate the output
        :param ** kwargs: Any keyword arguments for this module
        :raises TypeError: If provided an input type not supported
        :meta private:
        """
        self._prep()

        # Normalize input
        if isinstance(input, bytes):
            input = io.BytesIO(input)
        elif isinstance(input, str):
            input = io.BytesIO(input.encode())
        elif isinstance(input, io.TextIOWrapper):   # sys.stdin
            input = input.buffer

        # Use input's iterator or raise TypeError
        if input:
            input = iter(input)

            # Merge input if not iterating
            if not iterate:
                input = iter([b"".join(list(input))])

        # Call module
        results = self.handle(input, **kwargs)

        # Merge results if not generating
        if not generate:
            results = b"".join(list(results))

        return results


class Container(docker.models.containers.Container):
    """
    When a module requires more than a short python script, an
    ephemeral docker container can be used to perform more advanced
    functionality.
    """

    @classmethod
    def run(cls, image, command=None, **kwargs):
        """
        Build an ephemeral docker container from an image and run a command.
        This is simply a wrapper around `Docker-Py Container.run()`_, and
        keyword arguments can be passed in accordingly to customize the
        container.

        :param str image: The image to run
        :param str or list command: The command to run in the container
        :return: Container
        :rtype: docker.models.containers.Container

        Example:

        .. code-block:: python

            with Container.run("debian", command="date") as container:
                yield container.logs()

        .. _Docker-Py Container.run():
            https://docker-py.readthedocs.io/en/stable/containers.html#module-docker.models.containers
        """

        # Ensure the docker container will be ephemeral
        kwargs.update({
            "auto_remove" : True,
            "detach" : True,
        })

        # Generate and augment the ephemeral docker container
        container = client.containers.run(image, command, **kwargs)
        container.__class__ = cls
        return container

    def __enter__(self):
        # warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        return self

    def __exit__(self, etype, value, traceback):
        pass

    def __del__(self):
        try:
            self.kill()
        except docker.errors.APIError as e:
            pass

    def interact(self):
        """
        Attach to and interact with the docker container. Note that
        the container must have both :code:`stdin_open` and :code:`tty`
        set to True.

        Example:

        .. code-block:: python

            with Container.run(
                image="debian:latest",
                command="/bin/bash",
                stdin_open=True,
                tty=True) as container:

                container.interact()

        """
        proc = subprocess.Popen(["docker", "attach", self.name],
            stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        proc.communicate()


class Mount(tempfile.TemporaryDirectory):
    """
    When dealing with docker containers, a module may need to
    pass data between the host and the container. An Mount context
    manager can simplify that process by mounting a temporary
    directory to the container and reading or writing data
    to it as needed.
    """
    path = None
    mode = None

    def __init__(self, path, mode="rw", suffix=None, prefix=None, dir=None):
        """
        Initialize the Mount object with the provided mount conditions.

        :param str path: Path to mount the directory inside the container
        :param str mode: Permission to mount the directory with. Default: 'rw'
        :meta private:
        """
        # Docker cannot mount a mac's default temporary directory
        if dir is None and platform.system() == "Darwin":
            dir = "/tmp"

        # Create temporary directory
        super(Mount, self).__init__(suffix, prefix, dir)

        # Attach mount specification
        self.path = path
        self.mode = mode

    def __enter__(self):
        super(Mount, self).__enter__()
        return self

    @property
    def volumes(self):
        """
        Object used for mounting in docker containers. By placing
        this object in the 'volumes' keyword argument of a
        **Container**, the temporary directory will be mounted
        at the specified *mount* with the specified *mode*
        permissions.

        Example:

        .. code-block:: python

            with Mount("/data") as mount:
                with Container.run(
                    ...
                    volumes=mount.volumes,
                    ...

        """
        return {
            self.name : {
                "bind" : self.path,
                "mode" : self.mode,
            }
        }

    def open(self, file, *args, **kwargs):
        """
        Open a file in the temporary directory. Simply a wrapper around
        `open() <https://docs.python.org/3/library/functions.html#open>`_
        that deals with files inside the temporary directory.

        :param str file: Relative path to file within directory / mount
        :param str mode: Mode with which the file is opened
        :param * args: Rest of the arguments for
            `open() <https://docs.python.org/3/library/functions.html#open>`_
        :param ** kwargs: Rest of the keyword arguments for
            `open() <https://docs.python.org/3/library/functions.html#open>`_
        :return: file
        :rtype: file-like object

        Example:

        .. code-block:: python

            with Mount("/data") as mount:
                with mount.open("input", "wb") as f:
                    f.write(b"data")
        """
        return open(os.path.join(self.name, file), *args, **kwargs)
