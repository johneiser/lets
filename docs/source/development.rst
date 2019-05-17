
Development
===========

Participate in the development of **lets** modules by following the guidelines below and submitting pull requests to the `Github <https://github.com/johneiser/lets>`_ repository master branch.

======
Module
======

As a framework, most functionality takes the form of a *module*.  Modules are located in the *lets/modules* directory and are located in a strategically descriptive directory structure representing a brief summary of their functionality.

   *<verb>/[descriptor/]subject/[descriptor/]<module>*

For example, *encode/base64*, *generate/ssl/certificate* and *format/bash/python* do a good job of describing their functionality purely by their location in the directory structure and will be easy to find when using the framework.

.. autoclass:: lets.module.Module


Functionality
^^^^^^^^^^^^^

A module takes input (as bytes) and configuration options (as a dict), executes some functionality, and returns some output (as a generator of bytes).  Overload the ``Module.do`` function to detail this functionality.

.. automethod:: lets.module.Module.do

Logging
^^^^^^^

Logging can be done with ``self.info``, ``self.warn``, and ``self.error`` (``self.info`` will only be printed if the *verbose* flag is set).  Be sure to handle exceptions by using ``self.throw(e)`` to help specify the module in which the exception originated.

.. automethod:: lets.module.Module.info

.. automethod:: lets.module.Module.warn

.. automethod:: lets.module.Module.error

.. automethod:: lets.module.Module.throw

Options
^^^^^^^

To expose configuration options for the module, overload the ``Module.usage`` function to produce an `ArgumentParser <https://docs.python.org/3/library/argparse.html>`_ object, which will parse the input delivered to the bash interface.  Note that the python interface will not be affected by this, so be sure to also validate configuration options within the module's functionality.

.. automethod:: lets.module.Module.usage


Testing
^^^^^^^

Each module is also a `TestCase <https://docs.python.org/3/library/unittest.html#unittest.TestCase>`_, so make sure to overload the ``test`` function to perform some unit tests on the module's functionality.

.. automethod:: lets.module.Module.test


Example
^^^^^^^

Here is an example module illustrating these concepts:

.. literalinclude:: ../../lets/modules/sample/mymodule.py
   :language: python


=========
Extension
=========

Modules can be *extended* to inherit extra capabilities.  For example, modules that cannot solely rely on just a python script can inherit **DockerExtension**.  DockerExtension maintains a list of docker images required for the module and provides methods and classes to enable the use of docker containers.

.. autoclass:: lets.extensions.docker.DockerExtension
   :noindex:
   :members:

``DockerExtension.Container`` is simply a context manager wrapper around `Docker-Py Container 'run' <https://docker-py.readthedocs.io/en/stable/containers.html#module-docker.models.containers>`_.  Use it to instantiate and interact with an ephemeral docker container.

Example
^^^^^^^

Here is an example docker module illustrating these concepts:

.. literalinclude:: ../../lets/modules/sample/mydockermodule.py
   :language: python

Check out the :doc:`extensions` available to each of the many :doc:`modules`.
