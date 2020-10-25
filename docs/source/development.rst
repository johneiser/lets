Development
===========

As a framework, **lets** is composed of a series of modules, each implementing its own independent functionality. The primary component of a module, therefore, is the :py:class:`Module <lets.__module__.Module>` class.

.. autoclass:: lets.__module__.Module


Handle
------

The place to start when creating a module is its primary function, :py:meth:`handle <lets.__module__.Module.handle>`.


.. automethod:: lets.__module__.Module.handle


Arguments
---------

If your module takes any special arguments, implement the *class method* :py:meth:`add_arguments <lets.__module__.Module.add_arguments>`.

.. automethod:: lets.__module__.Module.add_arguments


Logging
-------

If you need to present any information to the user that should not be included in the output buffer, use the :py:attr:`logger <lets.__module__.Module.log>`.

.. autoproperty:: lets.__module__.Module.log

Example
-------

The following module performs a relatively straight-forward task: *any input data will be flipped in reverse*. To complicate things a bit, the module allows the user to specify the size of chunk which should be rearranged.

.. literalinclude:: ../../lets/sample/mymodule.py


Docker
------

As dandy as it is chaining small python scripts together, the true leverage **lets** provides is `docker <https://docs.docker.com/get-started/overview/>`_ integration. Each module has the ability to use one or more ephemeral docker :py:class:`containers <lets.__module__.Container>` to perform its functionality.

.. autoclass:: lets.__module__.Container
    :members: run


If the module does use any docker containers, make sure to list its required :py:attr:`images <lets.__module__.Module.images>` in the class definition.

.. autoproperty:: lets.__module__.Module.images


Interacting with Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There may be some situations where you want the user to be able to :py:meth:`interact <lets.__module__.Container.interact>` with the docker container.

.. automethod:: lets.__module__.Container.interact


Communicating with Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to pass data in and out of a docker container, we need to use a :py:class:`mount <lets.__module__.Mount>`.

.. autoclass:: lets.__module__.Mount
    :members:

Docker Example
--------------

The following module performs the following task: *any input data will be presented in an interactive hex editor, and whatever is saved will be passed along as output*.

Before we cover the module, we need to prepare the necessary docker image. In this case, we'll use a Debian image with :code:`hexedit` installed. We place the following file at :code:`lets/__images__/local/sample/Dockerfile`:

.. literalinclude:: ../../images/local/sample/Dockerfile


With the Dockerfile in place, we can construct the module and trust that **lets** will find and build the image before the module gets executed.

.. literalinclude:: ../../lets/sample/mydockermodule.py


