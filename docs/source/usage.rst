
Usage
=====

**lets** can be used in a variety of different environments, but the pattern will always be the same. Some :code:`input` will be provided to a :code:`module`, which will perform some function with :code:`options` to produce an :code:`output`.

.. code-block:: bash

    [input] | lets <module> [options]

The interfaces available are described in more detail, below.


.. _Bash:

====
Bash
====

.. automodule:: lets.__main__


.. _Python:

======
Python
======

.. autofunction:: lets.do

.. autofunction:: lets.help

.. autofunction:: lets.usage



.. _HTTP API:

========
HTTP API
========

.. automodule:: lets.modules.listen.serve.lets.http


=============
Customization
=============


The following environment variables are also available to customize various aspects of **lets**:

- :code:`LETS_DEBUG` *(flag)*: Print all logs, regardless of whether :code:`verbose` is specified
- :code:`LETS_NOCACHE` *(flag)*: Prevent the creation of python cache files for modules
- :code:`LETS_COMMUNITY` *(flag)*: Enable importing modules from other :code:`lets_*` packages
- :code:`LETS_TEMPDIR` *(str)*: Use the specified directory for mounting files inside docker containers

To get started making your own modules, refer to the :doc:`Development <development>` documentation.