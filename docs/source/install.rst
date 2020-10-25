Install
=======

Requirements
------------

**lets** uses python3 and python3-pip, so make sure they are installed.

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install python3 python3-pip -y


**lets** is built on top of `docker <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_, so make sure it is installed. You may need to log out and back in for this to take effect.

.. code-block:: bash

    $ curl -fsSL https://get.docker.com | sudo sh
    $ sudo usermod -aG docker $USER


Release
-------

Install the latest stable release of **lets** using pip3.

.. code-block:: bash

    $ pip3 install docker-lets


Extensions can also be installed with pip3.

.. code-block:: bash

    $ pip3 install docker-lets-pentest


Activate *tab-completion* for bash to browse available modules.

.. code-block:: bash

    $ lets support/autocomplete bash >> ~/.profile
    $ source ~/.profile
    $ lets sample/my[TAB][TAB]
    sample/mydockermodule   sample/mymodule


With **lets** installed, refer to the :doc:`Usage <usage>` documentation to get started.

Source
------

To get the absolute latest version, maybe to develop and contribute your own modules, you can install **lets** directly by downloading the `source <https://github.com/johneiser/lets>`_.

.. code-block:: bash

    $ git clone https://github.com/johneiser/lets
    $ pip3 install -e ./lets/


You can also download module extensions directly.

.. code-block:: bash

    $ git clone https://github.com/johneiser/lets_pentest
    $ pip3 install -e ./lets_pentest/

Refer to the :doc:`Development <development>` documentation for making your own modules.
