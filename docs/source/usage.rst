
Usage
=====

**lets** can be used in a variety of different environments.

=============
Bash Terminal
=============

**lets** general help can be viewed with the '-h' flag.

.. code-block:: bash

   $ lets -h
   usage: [input] | lets [-h] <module> [options]

**lets** module specific help can also be viewed with the '-h' flag.

.. code-block:: bash

   $ lets encode/base64 -h
   usage: base64 [-h] [-v]

In a bash terminal, modules can be chained together using pipes to produce unique sequences of functionality.  For example, the command below takes a string, base64 encodes it, and base64 decodes it back.

.. code-block:: bash

   $ echo -n "abcd" \
         | lets encode/base64 -v \
         | lets decode/base64 -v
   [+] |Base64| Running module with 4 bytes and options: {'verbose': True}
   [+] |Base64| Running module with 8 bytes and options: {'verbose': True}
   abcd


Every module has a verbose flag available by default. With the verbose flag set, extra information is logged to stderr in a way that does not interfere with the content being passed from one module to the next.

===========
Bash Script
===========

To save time, sequences of modules that are particularly long or that often run together can be put into a bash script, or *workflow*. Here is the same sequence we saw before:

.. literalinclude:: ../../workflows/sample.sh
   :language: bash

======
Python
======

If a sequence of modules requires a little more attention (like condition handling), a python script can also serve as a workflow. In place of 'lets' in bash, we have 'lets.do' in python, as well as 'lets.help', 'lets.list', and 'lets.exists'. Use help(lets) in python to find out more.

.. autofunction:: lets.do

.. literalinclude:: ../../workflows/sample.py
   :language: python

========
REST API
========

**lets** can also be served remotely as a rest api.  Modules can be accessed with a request to /lets/<module> with input data in the body and configuration options in the url query string.  Note that this is only valid for non-interactive modules.

.. code-block:: bash

   $ lets listen/serve/lets/http -v -p 8080
   # Listening...

.. literalinclude:: ../../workflows/sample_api.sh
   :language: bash

=============
Customization
=============

If your environment requires customization, **lets** exposes a number of variables to the environment.

.. list-table:: Environment variables
   :widths: 25 25 50
   :header-rows: 1

   * - Key
     - Default Value
     - Purpose
   * - LETS_WORKDIR
     - <package>/data
     - Defines where **lets** will place temporary files, often used to mount content into docker containers. You may want to customize this when dealing with large content.
   * - LETS_DEBUG
     - False
     - Signals **lets** to always print extra information, as if '-v' had been passed to every module.
   * - LETS_NOCACHE
     - False
     - Configures **lets** to not produce __pycache__/ everywhere, when working with source.

Browse the *lets/modules* folder, use bash tab-completion, or check out :doc:`modules` to see what modules are available.  If you're interested in building your own modules and contributing to the framework, refer to :doc:`development`.