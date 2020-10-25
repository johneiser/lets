from lets.__module__ import Module
from flask import Flask, request
import os, sys, types, ssl, importlib

class Http(Module):
    """
    Serve the lets framework over an HTTP API.

    Usage:
        $ lets() {
            curl -skL --data-binary @- "http://localhost:5000/lets/$1";
            }
        $ echo "abcd" | lets "encode/base64?generate=True"
    """

    @classmethod
    def add_arguments(self, parser):
        parser.add_argument("--interface", type=str, help="interface to listen on", default="0.0.0.0")
        parser.add_argument("-p", "--port", type=int, help="port to listen on", default=5000)
        parser.add_argument("-s", "--secure", action="store_true", help="use ssl")
        parser.add_argument("-k", "--key", type=str, help="use ssl key")
        parser.add_argument("-c", "--certificate", type=str, help="use ssl certificate")

    def handle(self, input, interface="0.0.0.0", port=5000, secure=False, key=None, certificate=None):
        
        # Import framework
        app = Flask(__name__)

        # Build request handler
        @app.route("/lets/<path:module>", methods=["GET", "POST"])
        def api(module=None):
            
            try:
                # Create copy of request arguments
                kwargs = dict(request.args)
                data = request.get_data(cache=False) or None

                # Find module
                module = os.path.join("lets", module.strip("/"))
                path = module.replace(os.path.sep, os.path.extsep)
                mod = importlib.import_module(path)

                # Execute module
                results = mod(data, **kwargs)

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
            except (ImportError, AssertionError) as e:
                self.log.error(e)
                return b"", 404

            # Handle any errors coming from module
            except Exception as e:
                self.log.exception(e)
                return str(e), 500

        # Generate SSL context, if necessary
        context = None
        if secure:
            context = "adhoc"
            if key and certficate:
                context = ssl.SSLContext()
                context.load_cert_chain(certificate, key)
            elif key:
                self.log.warning("Missing ssl certificate, continuing with self-signed certificate")
            elif certificate:
                self.log.warning("Missing ssl key, continuing with self-signed certificate")

        # Launch server
        app.run(interface, port, ssl_context=context)

        return iter(())
