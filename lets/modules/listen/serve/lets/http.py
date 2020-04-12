"""

**Lets** can be served remotely as an HTTP API. Modules can be accessed
with an HTTP GET or POST request to:

    http(s)://:code:`host`::code:`port`/lets/:code:`module`

with input data in the body and options in the url query string.

.. code-block:: bash

    $ lets listen/serve/lets/http -p 5000
    # Listening...

.. code-block:: bash

    $ lets() {
        curl -skL --data-binary @- "http://localhost:5000/lets/$1";
        }
    $ echo "abcd" | lets "encode/base64?generate=true"
    YWJjZAo=

"""
from lets.module import Module
from lets.logger import log
from unittest import TestCase
from flask import Flask, request
import sys, types, ssl

class Http(Module):
    """
    Serve the lets framework over an HTTP API.
    """

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("--interface", type=str, help="interface to listen on", default="127.0.0.1")
        parser.add_argument("-p", "--port", type=int, help="port to listen on", default=5000)
        parser.add_argument("-s", "--ssl", action="store_true", help="use ssl", default=False)
        parser.add_argument("--ssl-key", type=str, help="use ssl key", default=None)
        parser.add_argument("--ssl-cert", type=str, help="use ssl certificate", default=None)
        parser.add_argument("--path", type=str, help="api path prefix (default='%(default)s')", default="/lets/")

    def do(self, verbose, interface, port, ssl, ssl_key, ssl_cert, path, **kwargs):
        if self.has_input():
            log.debug("Ignoring supplied input data")

        path = path.strip("/") if path else "lets"

        import lets
        app = Flask(__name__)

        # Build request handler
        @app.route("/%s/" % path, methods=["GET", "POST"])
        @app.route("/%s/<path:module>" % path, methods=["GET", "POST"])
        def do(module=None):
            """
            Handle a request over the HTTP API.

            :param module: Module = request.path
            :param input: Input = request.data
            :param **options: Options = request.args
            """
            try:
                # Create copy of request arguments
                kwargs = dict(request.args)

                # Ensure server-side arguments remain set
                kwargs["verbose"] = verbose

                # Handle help
                if kwargs.get("help"):
                    return lets.help(module), 200

                data = request.get_data(cache=False) or None

                # Execute module (raises ImportError, ValueError, TypeError, KeyError)
                results = lets.do(module, data, **kwargs)

                # Return empty results
                if not results:
                    return b"", 200

                # Return generated results
                elif isinstance(results, types.GeneratorType):
                    response = b""
                    for result in results:
                        response += result
                        if not response.endswith(b"\n"):
                            response += b"\n"
                    return response, 200

                # Return non-generated results
                else:
                    return results, 200

            # Handle failure to find module
            except ImportError as e:
                log.error(str(e))
                return f"error: {e}\n" + lets.usage(), 400

            # Handle any errors coming from module
            except Exception as e:
                log.error(str(e))
                return f"error: {e}\n" + lets.usage(module), 400

        # Generate SSL context, if necessary
        context = None
        if ssl:
            context = "adhoc"
            if ssl_key and ssl_cert:
                context = ssl.SSLContext()
                context.load_cert_chain(ssl_cert, ssl_key)
            elif ssl_key:
                log.warn("Missing ssl certificate, continuing with self-signed certificate")
            elif ssl_cert:
                log.warn("Missing ssl key, continuing with self-signed certificate")

        # Launch server
        app.run(interface, port, ssl_context=context)


class HttpTests(TestCase):

    processes = []
    stdout = None
    stderr = None

    @classmethod
    def setUpClass(cls):
        """Start HTTP API."""
        
        # Temporarily replace standard output
        import sys, io
        cls.stdout = sys.stdout
        cls.stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        # Run HTTP API in the background
        import lets, multiprocessing, time
        process = multiprocessing.Process(
            target=lets.do,
            args=("listen/serve/lets/http",),
            kwargs={"port" : 5000})
        process.start()
        cls.processes.append(process)
        time.sleep(4)

    @classmethod
    def tearDownClass(cls):
        """Stop HTTP API."""

        # Restore standard output
        import sys
        sys.stdout = cls.stdout
        sys.stderr = cls.stderr

        # Clean up running processes
        for process in [p for p in cls.processes]:
            if process.is_alive():
                process.terminate()
                process.join()
            cls.processes.remove(process)

    # TODO: listen/serve/lets/http tests    
