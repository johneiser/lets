
lets
====

A modular framework for arbitrary action, **lets** enables tasks of varying complexity to be chained together with a simple and consistent interface.

Each module accepts :code:`input` and :code:`options`, executes some functionality, and returns some :code:`output`.

.. code-block:: bash

   [input] | lets <module> [options]

In this manner, modules can be *chained* together, allowing completely unrelated functionality to work together seamlessly. Modules can be as simple as base64 encoding or reasonably complex with docker integration.

Take a deeper look with :doc:`usage` or get started with :doc:`install`.

----------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   usage
   development


.. toctree::
   :maxdepth: 1

   changelog


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
