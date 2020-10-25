Usage
=====

**lets** can be used in a variety of different environments, but the pattern will always be the same. Some :code:`input` will be provided to a :code:`module`, which will perform some function with :code:`options` to produce an :code:`output`.

.. code-block:: bash

    [input] | lets <module> [options]


The interfaces available are described more in detail, below.

.. _Bash:

Bash
----

Once :doc:`installed <install>`, **lets** becomes available as a command in the bash terminal.

.. code-block:: bash

    $ lets -h
    usage: lets [-h] [-i] [-g] [-o OUTPUT] [-v] module ...

    positional arguments:
        module                module to use
        options               module options

    optional arguments:
        -h, --help            show this help message and exit
        -i, --iterate         iterate over input
        -g, --generate        generate each output
        -o OUTPUT, --output OUTPUT  output to file
        -v, --verbose         print debug info


With :doc:`bash tab-completion <install>` configured, :code:`[TAB]` can be used to browse available modules.

.. code-block:: bash

    $ lets sample/my[TAB][TAB]
    sample/mydockermodule   sample/mymodule


Each module also provides its own help text.

.. code-block:: bash

    $ lets encode/base64 -h

    usage: encode/base64 [-h] [-i] [-g] [-o OUTPUT] [-v]

    Base64 encode the provided data.

    optional arguments:
        -h, --help            show this help message and exit
        -i, --iterate         iterate over input
        -g, --generate        generate each output
        -o OUTPUT, --output OUTPUT  output to file
        -v, --verbose         print debug info
    

By default, when invoking a module from the bash interface, input is pulled from :code:`stdin`. This enables the two most common ways of passing data to a module, shown below:

.. code-block:: bash

    $ echo 'input' | lets encode/base64     # Input bytes
    aW5wdXQK

    $ lets encode/base64 < file.txt         # Input file
    aW5wdXQK


:code:`iterate` and :code:`generate` provide subtle adjustments to the way a module handles input and output data. :code:`iterate` will cause the module to perform its functionality for each line as opposed to all at once, and :code:`generate` will cause the module to generate any output as it becomes available, adding newlines if necessary. The following example demonstrates this:

.. code-block:: bash

    $ # Process all input, return all output
    $ echo -ne "abcd\nefgh\n" | lets encode/base64
    YWJjZAplZmdoCg==$

    $ # Process all input, generate each output
    $ echo -ne "abcd\nefgh\n" | lets encode/base64 -g
    YWJjZAplZmdoCg==
    $

    $ # Process each input, generate each output
    $ echo -ne "abcd\nefgh\n" | lets encode/base64 -ig
    YWJjZAo=
    ZWZnaAo=
    $
    
    $ # Process each input, return all output
    $ echo -ne "abcd\nefgh\n" | lets encode/base64 -i
    YWJjZAo=ZWZnaAo=$


The sum effect is the ability to *chain* modules together in various ways.

.. code-block:: bash

    $ # Convert data from one format to another
    $ echo 'abcd' | lets encode/base64 | lets decode/base64 -g
    abcd

    $ # Filter and react to data
    $ echo "192.168.1.0/24" \
        | lets scan/network/ping -ig | tee hosts.txt \
        | lets scan/network/services -ig > services.txt

    $ # Configure and run services
    $ lets generate/config/ftp -u admin -p admin \
        | lets listen/serve/ftp -p 2021
    [+] Listening ...


Python
------

In python, modules can simply be imported and called directly, and the input can be provided in a number of different formats.

.. code-block:: python

    import lets.base64.encode as encode

    result = encode("string")
    result = encode(b"bytes")
    result = encode([b"list"])
    with open("input.txt", "rb") as file:
        result = encode(file)


:code:`iterate` and :code:`generate`, as in bash, provide subtle adjustments to the way a module handles input and output data. :code:`iterate` will cause the module to perform its functionality for each line or item as opposed to all at once, and :code:`generate` will cause the module to generate any output as it becomes available. The following example demonstrates this:

.. code-block:: python

    >> import lets.base64.encode as encode
    
    >> encode([b"abcd", b"efgh"])
    b'YWJjZGVmZ2g='

    >> list(encode([b"abcd", b"efgh"], generate=True))
    [b'YWJjZGVmZ2g=']

    >> list(encode([b"abcd", b"efgh"], iterate=True, generate=True))
    [b'YWJjZA==', b'ZWZnaA==']

    >> encode([b"abcd", b"efgh"], iterate=True)
    b'YWJjZA==ZWZnaA=='



HTTP API
--------

**lets** can be served remotely as an HTTP API. Modules can be accessed with an HTTP GET or POST request to:

    http(s):// :code:`host` : :code:`port` / :code:`module` ? :code:`kwargs`

with input data in the body and options in the url query string.

.. code-block:: bash

    $ lets listen/serve/lets/http -p 5000
    Listening...

.. code-block:: bash

    $ lets() {
        curl -skL --data-binary @- "http://localhost:5000/lets/$1";
        }
    $ echo "abcd" | lets "encode/base64?generate=True"
    YWJjZAo=


To get started making  your own modules, refer to the :doc:`Development <development>` documentation.
