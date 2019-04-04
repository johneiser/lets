
Modules
=======

.. autoclass:: lets.modules.template.mydockermodule.MyDockerModule

   Docker images: ['ubuntu:latest']

.. code-block:: bash

   usage: mydockermodule [-h] [-v] [-q] [-u]


.. autoclass:: lets.modules.template.mymodule.MyModule

.. code-block:: bash

   usage: mymodule [-h] [-v] [-q] [-u]


.. autoclass:: lets.modules.encode.base64.Base64

.. code-block:: bash

   usage: base64 [-h] [-v] [-q]


.. autoclass:: lets.modules.decode.base64.Base64

.. code-block:: bash

   usage: base64 [-h] [-v] [-q]


.. autoclass:: lets.modules.generate.payload.windows.x64.messagebox.Messagebox

   Docker images: ['tools/metasploit:latest']

.. code-block:: bash

   usage: messagebox [-h] [-v] [-q] [-t TITLE] [-m MESSAGE]
                  [-i {NO,ERROR,INFORMATION,WARNING,QUESTION}]
                  [-e {seh,thread,process,none}]


.. autoclass:: lets.modules.generate.payload.windows.x86.messagebox.Messagebox

   Docker images: ['tools/metasploit:latest']

.. code-block:: bash

   usage: messagebox [-h] [-v] [-q] [-t TITLE] [-m MESSAGE]
                  [-i {NO,ERROR,INFORMATION,WARNING,QUESTION}]
                  [-e {seh,thread,process,none}]

