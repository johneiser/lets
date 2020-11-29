import os, sys, argparse, logging, types, docker, tempfile, platform, subprocess, io, unittest, queue, time, pkg_resources

log = logging.getLogger(__package__)
client = None


def iter_module_paths():
    """
    Iterate through packages that have registered a modules directory in the
    following way and return their full path.

    .. code-block:: python

        setup(
            ...
            entry_points = {
                "lets" : [ "modules=[PACKAGE NAME]:[PATH TO MODULES]" ],
            }
            ...
        )
    """
    paths = []
    for entry in pkg_resources.iter_entry_points(__package__, "modules"):
        for attr in entry.attrs:
            path = os.path.join(entry.dist.location, entry.module_name, attr)
            if path not in paths:
                yield path
                paths.append(path)

def iter_module_packages():
    """
    Iterate through packages that have registered a modules directory in the
    following way and return their full package name.

    .. code-block:: python

        setup(
            ...
            entry_points = {
                "lets" : [ "modules=[PACKAGE NAME]:[PATH TO MODULES]" ],
            }
            ...
        )
    """
    packages = []
    for entry in pkg_resources.iter_entry_points(__package__, "modules"):
        for attr in entry.attrs: 
            package = os.path.join(entry.module_name, attr)
            package = package.replace(os.path.sep, os.path.extsep)
            package = package.strip(os.path.extsep)
            if package not in packages:
                yield package
                packages.append(package)

class ModuleMeta(type):
    """
    Enable a module to register itself as callable upon import.
    """
    def __init__(cls, name, bases, namespace):
        super(ModuleMeta, cls).__init__(name, bases, namespace)

        # Load module as callable
        if cls.__module__ != __name__:
            sys.modules[cls.__module__].__class__ = cls


class ModuleLogger(logging.LoggerAdapter):
    """
    Add module context while logging.
    """
    def process(self, msg, kwargs):
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
    delimiter = b"\n"   # Used to separate generated output

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
        _,_,module = cls.__module__.replace(os.path.extsep, os.path.sep).partition(os.path.sep)
        parser = argparse.ArgumentParser(module,
                description=cls.__doc__,
                formatter_class=argparse.RawTextHelpFormatter)
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
        global client

        # Confirm docker is installed
        if images or self.images:
            if not client:
                client = docker.from_env()
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
            results = b"".join(list(results)) if results else b""

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
        :param str|list command: The command to run in the container
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
        
        # Ignore errors for missing container
        if etype in [docker.errors.NotFound]:
            return True

        # Remove container if still running
        try:
            self.kill()
        except (docker.errors.APIError, docker.errors.NotFound) as e:
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

    def output(self, **kwargs):
        """
        Wait for the container to complete and return its output.

        Example:

        .. code-block:: python

            with Container.run(
                image="debian:latest",
                command="date") as container:

                yield container.output()
        """
        kwargs.update({
            "stream" : True,
            "timestamps" : False,
            "follow" : True,
            })

        return b"".join(list(self.logs(**kwargs)))
        

class Mount(tempfile.TemporaryDirectory):
    """
    When dealing with docker containers, a module may need to
    pass data between the host and the container. A Mount context
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
        this object in the 'volumes' keyword argument of
        **Container.run**, the temporary directory will be mounted
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


class IterWriter(io.BytesIO):
    """
    Provide a virtual file interface to write to which can then be interated from.

    This interface can be useful when a tool expects to write to a file, but you
    want to yield the data as output.

    .. code-block:: python

        with IterWriter() as f:
            f.write(b"data")

            for data in f:
                yield data
    """
    def __init__(self, *args, **kwargs):
        super(IterWriter, self).__init__(*args, **kwargs)
        self.queue = queue.Queue()

    def write(self, data):
        """
        Write the given bytes to the iterator.

        :param bytes data: data to write
        """
        self.queue.put(data)

    def writelines(self, lines):
        """
        Write a list of lines to the iterator.

        :param list lines: lines to write
        """
        for line in lines:
            self.write(line)

    def __iter__(self):
        return self

    def __next__(self):

        # Only stop when file is closed and queue is empty
        if self.closed and self.queue.empty():
            raise StopIteration()
        return self.queue.get()


class IterReader(io.BytesIO):
    """
    Buffer an iterator and provide a virtual file interface to read from.

    This interface can be useful when a tool expects to read from a file,
    but you want to use your input generator.

    .. code-block:: python

        with IterReader(input) as f:
            while True:
            header = f.read(4)
            message = f.readline()
    """
    def __init__(self, iterator, *args, **kwargs):
        super(IterReader, self).__init__(*args, **kwargs)
        self.iterator = iterator

    def read(self, count=-1):
        """
        Read from iterator up to count.

        :param int count: maximum bytes to read (-1 for all)
        :return: iterator content
        :rtype: bytes
        """
        # Read entire global buffer
        data = super(IterReader, self).read()
        self.seek(0)
        self.truncate()

        # Add data from iterator
        while len(data) < count or count < 0:
            try: data += next(self.iterator)
            except StopIteration: break

        # Store excess data in global buffer
        if count > 0 and len(data) > count:
            self.write(data[count:])
            self.seek(0)
            data = data[:count]

        return data

    def readall(self):
        """
        Read over entire iterator.

        :return: iterator content
        :rtype: bytes
        """
        return self.read(-1)

    def readline(self):
        """
        Return a single iterator.

        :return: iteration
        :rtype: bytes
        """
        # Read entire global buffer
        data = super(IterReader, self).read()
        self.seek(0)
        self.truncate()

        # Add data from iterator
        try: data += next(self.iterator)
        except StopIteration: pass

        return data

    def readlines(self, hint=None):
        """
        Return a list of each iteration.

        :param int hint: maximum size of list
        :return: all iterations
        :rtype: list
        """
        if hint is None or hint <= 0:
            return list(self)
        n = 0
        lines = []
        for line in self:
            lines.append(line)
            n += len(line)
            if n >= hint:
                break
        return lines

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line


class IterSync(io.BytesIO):
    """
    Buffer an iterator and re-iterate according to time of arrival.

    For example, a normal iterator will split a file based on newlines.

    .. code-block:: python

        for line in input:
            self.log.info("Next line: %s", line)

    A synchronized iterator will instead split based on time of arrival.

    .. code-block:: python

        for data in IterSync(input):
            self.log.info("Received more: %s", data)
    """
    def __init__(self, iterator, interval=0.1):
        self.iterator = iterator
        self.interval = interval

        # Set non-blocking, if available
        if hasattr(self.iterator, "fileno"):
            os.set_blocking(self.iterator.fileno(), 0)

    def __iter__(self):
        return self

    def __next__(self):
        data = b""

        # Accumulate all available data
        while True:
            try:
                data += next(self.iterator)

            # Handle exhausted iterator
            except StopIteration as e:
                if hasattr(self.iterator, "read"):
                    peek = self.iterator.read()
                    if peek is None:
                        if data: break      # Return what we have
                        else: time.sleep(self.interval) # Wait for more data
                    elif not peek: break    # Return what we have
                    else: data += peek      # Return what we have
                else:
                    if data: break          # Return what we have
                    else: raise e           # Stop iteration

        if not data: raise StopIteration()  # Stop iteration
        return data


class TestCase(unittest.TestCase):
    """
    Functionality should be verified by a series of tests, which
    can be included directly in the module as a TestCase.

    .. code-block:: python

        class MyModule(Module):
            ...

        class MyModuleTests(TestCase):
            def test_simple(self):
                self.assertTrue(True)
    """
    images = []
    """
    Specify required docker images.

    .. code-block:: python

        class MyModuleTests(TestCase):
            images = ["python:2", "python:3"]
    """

    module = None
    """
    The neighboring module will already be imported.

    .. code-block:: python

        class MyModuleTests(TestCase):
            def test_simple(self):
                data = bytes(range(0,256))
                result = self.module(data)
                ...
    """

    def setUp(self):
        """
        Make preparations before tests are called.

        :meta private:
        """
        import importlib
        self.module = importlib.import_module(self.__module__)
        self.module._prep(self.images)

