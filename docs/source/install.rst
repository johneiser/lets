
Install
=======

**lets** is tested on Ubuntu 16.04, some modules may not be available on all platforms.


============
Requirements
============

- `docker <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_
- python >= 3.5
- python3-pip


======
Stable
======

**lets** is built on top of `docker <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_, so make sure it is installed. You may need to log out and back in for this to take effect.

.. code-block::

    $ curl -fsSL https://get.docker.com | sudo sh
    $ sudo usermod -aG docker $USER


Install the latest stable release of **lets** using pip.

.. code-block::

    $ pip3 install docker-lets
    $ lets -h
    usage: lets [-h] [-v] [-i] [-g] module ...

Activate **lets** *tab-completion* for bash:

.. code-block::

    $ lets complete/bash >> ~/.profile
    $ source ~/.profile
    $ lets sample/my[TAB][TAB]
    sample/mydockermodule   sample/mymodule

Refer to the :doc:`Usage <usage>` documentation to get started, or `explore <https://johneiser.github.io/lets>`_ some of the available modules.

----------

======
Source
======

If you intend to contribute to the framework and develop your own modules, you can install the latest version of **lets** by downloading the `source <https://github.com/johneiser/lets>`_.

.. code-block::

    $ git clone https://github.com/johneiser/lets
    $ pip3 install -e ./lets/
    $ lets -h
    usage: lets [-h] [-v] [-i] [-g] module ...

Refer to the :doc:`Development <development>` documentation for making your own modules.