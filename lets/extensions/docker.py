"""

When the inherent functionality of a :py:class:`Module <lets.module.Module>` is not
sufficient for the task, an extension can be used to enable additional functionality.
One powerful example of this is the **Docker Extension**, which enables the use of
Docker containers in a module.

For example:

.. code-block:: python

    from lets.extensions.docker import Container, ImageDecorator

    @ImageDecorator("debian:latest")
    def do(self, **kwargs):

        with Container(
            image="debian:latest",
            command="date"
            ) as container:

            yield container.logs()

----------

"""
import os, sys, platform, tempfile, shutil, threading, docker, functools, subprocess, requests, warnings
from lets.logger import log, LEVEL_DEV
from lets.module import BASE_DIRS
from unittest import TestCase

if "LETS_TEMPDIR" in os.environ:
    path = os.environ.get("LETS_TEMPDIR")
    assert os.path.isdir(path), "Invalid temporary directory specified: %s" % path
    TEMP_DIR = os.path.abspath(path)
else:
    # Docker cannot mount a mac's default temporary directory
    TEMP_DIR = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()

class Container(object):
    """
    A module can use this context manager to produce and use an ephemeral
    docker container. This class and its functions are simply a wrapper
    around `Docker-Py Container.run()`_, and keyword arguments can be
    passed in accordingly to customize the container.

    For example, here is a container that fetches the date:

    .. code-block:: python

        with Container(
            image="debian:latest",
            command="date"
            ) as container:

            yield container.logs()

    .. _Docker-Py Container.run():
            https://docker-py.readthedocs.io/en/stable/containers.html#module-docker.models.containers
    """
    _container = None

    def __init__(self, **kwargs):
        """
        Initialize the container to be ephemeral.

        :param ** kwargs: Container customizations
        :meta private:
        """
        client = docker.from_env()
        
        # Ensure some necessary options are set
        kwargs.update({
            # Ephemeral
            "auto_remove" : True,
            # Asynchronous
            "detach" : True,
        })

        # Run the container
        self._container = client.containers.run(**kwargs)
        log.debug("Starting new %s docker container: %s", kwargs.get("image"), self._container.name)

    def __enter__(self):
        """
        Enter the context.

        :meta private:
        """
        # TODO: Why do these warnings occur?
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        return self

    def __exit__(self, etype, value, traceback):
        """
        Exit the context.

        :meta private:
        """
        pass

    def __del__(self):
        """
        Clean up the context by deleting any lingering containers.

        :meta private:
        """
        try:
            if self._container:
                self._container.kill()
        except docker.errors.APIError as e:
            log.log(LEVEL_DEV, str(e))

    def logs(self, **kwargs):
        """
        Return a generator of the container logs. Simply a wrapper around
        `Docker-Py Container.logs() <https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.logs>`_.

        :param bool stdout: Get STDOUT. Default :code:`True`
        :param bool stderr: Get STDERR. Default :code:`True`
        :param bool stream: Stream the response. Default :code:`False`
        :param bool timestamps: Show timestamps. Default :code:`False`
        :param tail: Output specified number of lines at the end of logs. Either an integer of number of lines or the string all. Default all
        :type tail: str or int
        :param since: Show logs since a given datetime or integer epoch (in seconds)
        :type since: datetime or int
        :param bool follow: Follow log output. Default :code:`False`
        :param until: Show logs that occurred before the given datetime or integer epoch (in seconds)
        :type until: datetime or int
        :return: Logs from the container
        :rtype: generator or bytes

        Example of getting entire command output:

        .. code-block:: python

            with Container(...) as container:
                yield container.logs()

        Example of a generating command output:

        .. code-block:: python

            with Container(...) as container:
                for line in container.logs(stream=True, follow=True):
                    yield line
        
        """
        try:
            return self._container.logs(**kwargs)

        # Handle no more container
        except docker.errors.NotFound as e:
            log.warn(str(e))

        except docker.errors.APIError as e:
            log.error(str(e))

    def wait(self, **kwargs):
        """
        Wait for the container to finish running. Simply a wrapper around
        `Docker-Py Container.wait() <https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.wait>`_.
        
        :param int timeout: Request timeout
        :param str condition: Wait until a container state reaches the given
            condition, either :code:`'not-running'` (default),
            :code:`'next-exit'`, or :code:`'removed'`

        Example:

        .. code-block:: python
        
            with Container(
                image="debian:latest",
                command="ping 8.8.8.8"
                ) as container:

                container.wait()
        
        """
        try:
            self._container.wait(**kwargs)

        # Handle no more container
        except docker.errors.NotFound as e:
            log.debug(str(e))

        # Handle timeout
        except requests.exceptions.ConnectionError as e:
            log.warn(str(e))

    def interact(self):
        """
        Connect stdin, stdout, and stderr to the container. Note that the container
        must have :code:`stdin_open` and :code:`tty` set to True.

        Example:

        .. code-block:: python

            with Container(
                image="debian:latest",
                command="/bin/bash",
                stdin_open=True,
                tty=True
                ) as container:

                container.interact()

        """
        proc = subprocess.Popen(
            ["docker", "attach", self._container.name],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr)
        proc.communicate()

    def exec(self, cmd, **kwargs):
        """
        Run the specified command inside the container. This is useful when paired
        with the bash command "sleep infinity". Simply a wrapper around
        `Docker-Py Container.exec_run() <https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.exec_run>`_.

        :param cmd: Command to be executed
        :type cmd: str or list
        :return: Exit-code and output of command
        :rtype: tuple(int, bytes)

        Example:

        .. code-block:: python
        
            with Container(
                image="debian:latest",
                command="sleep infinity"
                ) as container:

                err, result = container.exec("whoami")
                if not err:
                    yield result

        """
        try:
            return self._container.exec_run(cmd, **kwargs)
        
        # Handle no more container
        except docker.errors.NotFound as e:
            log.warn(str(e))

        except docker.errors.APIError as e:
            log.error(str(e))

class IO(object):
    """
    When dealing with one or more docker containers, a module may need
    to pass data between the host and the container. Use this context
    manager to simplify the process by creating a temporary directory
    that can then be mounted in the docker container.

    For example:

    .. code-block:: python

        # Open the temporary directory
        with IO(mount="/data") as io:

            # Write input data
            with io.open("input", "wb") as f:
                f.write(b"test")

            # Run container command with mount
            with Container(
                image="debian:latest",
                volumes=io.volumes,
                command="cp /data/input /data/output"
            ) as container:

                # Wait for container command to finish
                container.wait()

            # Read output data
            with io.open("output", "rb") as f:
                yield f.read()
    """
    path = None
    mount = None
    mode = None

    def __init__(self, mount, mode="rw"):
        """
        Initialize the IO object with the provided mount conditions.

        :param str mount: Path to mount the directory inside the container
        :param str mode: Permission to mount the directory with. Default: 'rw'
        :meta private:
        """
        self.mount = mount
        self.mode = mode
        self.path = tempfile.TemporaryDirectory(dir=TEMP_DIR)

    def __enter__(self):
        """
        Enter context.

        :meta private:
        """
        self.path.__enter__()
        return self

    def __exit__(self, etype, value, traceback):
        """
        Exit context.

        :meta private:
        """
        self.path.__exit__(etype, value, traceback)

    @property
    def volumes(self):
        """
        Object used for mounting in docker containers. By placing
        this object in the 'volumes' keyword argument of a
        **Container**, the temporary directory will be mounted
        at the initialized *mount* with the initialized *mode*
        permissions.

        :return: Mount object
        :rtype: dict
        
        Example:

        .. code-block:: python

            with IO("/data") as io:
                with Container(
                    ...
                    volumes=io.volumes,
                    ...
        """
        return {
            self.path.name : {
                "bind" : self.mount,
                "mode" : self.mode,
            }
        }

    def open(self, file, *args, **kwargs):
        """
        Open a file in the temporary directory. Simply a wrapper around
        `open() <https://docs.python.org/3/library/functions.html#open>`_
        that deals with files inside the temporary directory.

        :param str file: Relative path to file within directory / mount
        :param str mode: Mode in which the file is opened
        :param * args: Rest of the arguments for
            `open() <https://docs.python.org/3/library/functions.html#open>`_
        :param ** kwargs: Rest of the keyword arguments for
            `open() <https://docs.python.org/3/library/functions.html#open>`_
        :return: File object
        :rtype: file

        Example:

        .. code-block:: python

            with IO("/data") as io:
                with io.open("input", "wb") as f:
                    f.write(b"data")
 
        """
        return open(os.path.join(self.path.name, file), *args, **kwargs)


class ImageDecorator(object):
    """
    When dealing with docker containers, it is necessary to manage
    docker images. Some modules will use images available in the
    public repository, which would be automatically downloaded by the
    docker daemon, but others require further customization. That is
    where the **ImageDecorator** comes in. Adding this decorator to
    a function ensures that any specified docker images are pulled
    or built prior to execution.

    Just like :py:class:`modules <lets.module.Module>`, images can be
    locatedamong several searched local directories. Images are ingested
    from the following locations (in the following order):

    - Home directory: :code:`~/.lets/images/`
    - Package directory: :code:`<python>/site-packages/lets/images/`
    - Community package directories (if env["LETS_COMMUNITY"] is set):
        :code:`<python>/site-packages/lets_*/images/`

    If the build configuration for the image is not found in any of the
    local directories, it will then be searched for in the public
    docker repository.

    For example, if I wish to include the image :code:`local/tool` in
    my module, I would create :code:`~/.lets/images/local/tool/Dockerfile`
    and include the image tag in my module's :py:meth:`do <lets.do>`
    function, like so:

    .. code-block:: python

        @ImageDecorator("local/tool")
        def do(self, **kwargs):
            ...
    """
    _client = None

    def __init__(self, *images):
        """
        Initialize decorator with a list of images.

        :param * images: Images to fetch prior to execution
        :meta private:
        """
        self.images = images

    def __call__(self, func, *args, **kwargs):
        """
        Build a decorated wrapper function around the original function.

        :param function func: Original function
        :param * args: Original function arguments
        :param ** kwargs: Original function keyword arguments
        :return: Decorated wrapper function
        :rtype: function
        :meta private:
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
    def client(self):
        """
        Return a handle to the docker client.

        :return: Docker client
        :rtype: docker.client.DockerClient
        :meta private:
        """
        if not self._client:
            self._client = docker.from_env()

        # Confirm docker is installed
        try:
            self._client.ping()
        except docker.errors.APIError as e:
            raise AssertionError("Unable to connect to docker, is it installed?")

        return self._client

    def prep(self, images):
        """
        Prepare required docker images.
        
        :param list images: List of required docker images
        :raises AssertionError: If the image cannot be found or built
        :meta private:
        
        The process of identifying images happens in the following order:

        1. Check if image already exists
        2. Check if the image can be found and built locally
        at the following locations (in the following order):

            - Home directory: *~/.lets/images/*
            - Package directory: *<python>/site-packages/lets/images/*
            - Other lets_* package directories (if env["LETS_COMMUNITY"] is set)

        3. Check if the image can be pulled from the public docker
        repository
        """
        for tag in images:
            image = None
            client = self.client

            # Check if image already exists
            try:
                image = client.images.get(tag)
                if image is not None:
                    log.log(LEVEL_DEV, "Found required docker image: %s", image)
                    continue

            except docker.errors.ImageNotFound as e:
                log.log(LEVEL_DEV, str(e))

            except docker.errors.APIError as e:
                log.warn(str(e))

            # Check if image can be built locally
            try:
                [name,_,version] = tag.partition(":")
                for base in BASE_DIRS:
                    try:
                        path = os.path.join(base, "images", name)
                        if os.path.isdir(path):
                            log.info("Building image: %s", path)
                            client.images.build(tag=tag, path=path, pull=True)
                            break

                    except docker.errors.BuildError as e:
                        log.warn(str(e))
                    
                    except docker.errors.APIError as e:
                        log.warn(str(e))
                
                image = client.images.get(tag)
                if image is not None:
                    log.debug("Built required docker image: %s", image)
                    continue

            except docker.errors.ImageNotFound as e:
                log.log(LEVEL_DEV, str(e))

            # Check if image can be pulled remotely
            try:
                log.info("Pulling image: %s", tag)
                image = client.images.pull(tag)
                if image is not None:
                    log.debug("Pulled required docker image: %s", image)
                    continue

            except docker.errors.ImageNotFound as e:
                log.log(LEVEL_DEV, str(e))

            except docker.errors.APIError as e:
                log.error(str(e))

            raise AssertionError("Missing required docker image: %s", tag)

class DockerTests(TestCase):
    """
    Ensure docker extension works as expected.

    :meta private:
    """

    # TODO: docker tests
