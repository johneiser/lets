
Install
=======

============
Requirements
============

- Linux
- `Docker <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_ (tested with 18.09.2)
- Python3 (tested with Python v3.7.1)

Might also require:

- python3-dev
- gcc

===================
Virtual Environment
===================

It is highly recommended to use a `python virtual environment <https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv>`_ for this project.  For a quick reminder, here are the steps:

.. code-block::

   $ pip install virtualenv
   $ mkdir venv
   $ virtualenv -p python3 venv
   $ source venv/bin/activate
   (venv) $ python --version
   Python 3.7.1
   (venv) $ pip install --upgrade pip


**lets** itself uses a virtual environment, but solely for tab completion - it should be compatible with the python virtual environment and fine to use in tandem.


===========
From Source
===========

Use *git* to download **lets** from the `Github Repository <https://github.com/johneiser/lets>`_.  In your python virtual environment, make sure to install the python requirements with *pip*.

.. code-block::

   ~ $ git clone https://github.com/johneiser/lets
   ~ $ cd lets
   ~/lets $ pip install -r requirements.txt


To get started using **lets**, refer to the :doc:`usage`.  Or, to build your own modules and contribute to the framework, check out :doc:`development`.

