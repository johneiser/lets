
Install
=======

**lets** is tested on Ubuntu 16.04, some modules may not be available on all platforms.

============
Requirements
============

- `Docker <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_
- Python >= 3.5

======
Docker
======

**lets** is built on top of `docker <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_, so make sure it is installed. You may need to log out and back in for this to take effect.

.. code-block:: bash

    $ curl -fsSL https://get.docker.com | sudo sh
    $ sudo usermod -aG docker $USER


=================
Install Using Pip
=================

Install **lets**:

.. code-block:: bash

   $ pip3 install docker-lets


Activate **lets** *tab-completion* for bash:

.. code-block:: bash

   $ lets generate/support/completion/bash >> ~/.profile
   $ source ~/.profile
   $ lets sample/my[TAB][TAB]
   sample/mydockermodule    sample/mymodule


===================
Install From Source
===================

Use *git* to download **lets** from the `Github <https://github.com/johneiser/lets>`_ repository and install the python requirements with *pip*.

.. code-block:: bash
    
    ~ $ git clone https://github.com/johneiser/lets
    ~ $ cd lets
    ~/lets $ pip3 install -r requirements.txt

Enter the **lets** virtual environment in bash to enable *tab-completion*.

.. code-block:: bash

    ~/lets $ source lets/bin/activate
   (lets) ~/lets $ lets sample/my[TAB][TAB]
   sample/mydockermodule    sample/mymodule
   (lets) ~/lets $ lexit
    ~/lets $ 

**lets** uses a virtual environment solely for tab completion, it should be compatible with a python virtual environment and fine to use in tandem.



To get started using **lets**, refer to the :doc:`usage`.  Or, to build your own modules and contribute to the framework, check out :doc:`development`.

