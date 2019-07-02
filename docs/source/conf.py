# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os, sys, pprint, pkgutil
sys.path.insert(0, os.path.abspath('../..'))
sys.dont_write_bytecode = True

# -- Generate modules --------------------------------------------------------

from lets.module import Module
from lets.extensions.docker import DockerExtension

def generate_modules():

    # Header
    yield """
Modules
=======
"""

    for label in Module.identify_all():

        # Exclude samples
        if not label.startswith("lets.modules.sample"):

            # Instantiate module            
            mod = Module.instantiate(label)
            if mod:

                # Description
                yield """
.. autoclass:: %s.%s
""" % (label, mod.__class__.__name__)

                # Docker-Specific
                if isinstance(mod, DockerExtension):

                    yield """
   Docker images: %s
""" % (pprint.pformat(mod.images))

                # Usage
                yield """
.. code-block:: bash

   %s
""" % mod.usage().format_usage()

# Generate modules.rst
with open(os.path.sep.join([os.path.dirname(__file__), "modules.rst"]), "w") as f:
    for line in generate_modules():
        f.write(line)

# -- Generate extensions -----------------------------------------------------

import lets.extensions

def generate_extensions():

    # Header
    yield """
Extensions
==========
"""

    for importer, modname, ispkg in pkgutil.iter_modules(lets.extensions.__path__):
        if not ispkg:

            # Description
            yield """
.. automodule:: %s.%s
   :members:
""" % (lets.extensions.__package__, modname)

# Generate extensions.rst
with open(os.path.sep.join([os.path.dirname(__file__), "extensions.rst"]), "w") as f:
    for line in generate_extensions():
        f.write(line)

# -- Project information -----------------------------------------------------

project = 'lets'
copyright = '2019, johneiser'
author = 'johneiser'

# The full version, including alpha/beta/rc tags
with open(os.path.sep.join([os.path.abspath('../..'), "VERSION"]), "r") as f:
    release = f.read()

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
