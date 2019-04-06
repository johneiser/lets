
lets
====

A modular framework for arbitrary action, **lets** enables tasks of varying complexity to be chained together with a consistent and simple interface.

As a modular framework, each module accepts input and options, executes some functionality, and returns some output.

.. code-block:: bash

   [input] | lets <module> [options]


In this manner, modules can be *chained* together, allowing completely unrelated functionality to work together seamlessly.  Modules can be as simple as base64 encoding or reasonably complex with docker integration.

Let's take a deeper look with :doc:`usage`, or get started with :doc:`install`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   usage
   development
   modules
   changelog


========
Appendix
========

* :ref:`genindex`
* :ref:`search`
