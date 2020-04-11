
Samples
=======

Here are a few sample modules for reference.


========
Standard
========

The following module performs this relatively straight-forward task: *any input data will be flipped in reverse*. To complicate things a bit, the module allows the user to specify the size of chunk which should be rearranged. We build the following module at :code:`modules/sample/mymodule.py`:

.. literalinclude:: ../../lets/modules/sample/mymodule.py


======
Docker
======

This next module uses the docker extension to add an interesting piece of functionality: *any input data will be presented in an interactive hex editor, and whatever is saved will be passed along as output*.

Before we cover the module, we need to prepare the necessary docker image. In this case, we'll use a Debian image with :code:`hexedit` installed. We place the following file at :code:`images/local/sample/Dockerfile`:

.. literalinclude:: ../../lets/images/local/sample/Dockerfile

With the Dockerfile in place, we can construct the module and trust that **lets** will find and build the image before the module gets executed. We build the following module at :code:`modules/sample/mydockermodule.py`:

.. literalinclude:: ../../lets/modules/sample/mydockermodule.py

For further examples, check out the other `modules <https://johneiser.github.io/lets/>`_ included in the framework.
