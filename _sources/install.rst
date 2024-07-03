Install
=======

This section contains the instructions to install ``SciXTracer``

Using PyPI
----------

Releases are available in PyPI repository. We recommend using virtual environment.
Depending on the ``SciXTracer`` backend you are using you may need to install various packages.
For default local usage:

.. code-block:: shell

    python -m venv .venv
    source .env/bin/activate
    pip install scixtracer_local


From source
-----------

If you plan to develop ``SciXTracer`` or want to install locally from sources

.. code-block:: shell

    python -m venv .venv
    source .venv/bin/activate
    git clone https://github.com/scixtracer/scixtracer_local.git
    cd scixtracer_local
    pip install -e .

Configuration
-------------

SciXTracer works with a configuration file ``config.yml`` that setup the backend.
The backend is the part of SciXTracer that store the dataset data, annotations and metadata.

For a local configuration, create a ``config.yml`` file at the root directory where you run
your code and fill it with the content:

.. code-block:: yaml

    index:
      name: local
      workspace: ${workspace_dir}
    storage:
      name: local
      workspace: ${workspace_dir}
    metadata:
      name: local
      workspace: ${workspace_dir}
    runner:
      name: local

and change `${workspace_dir}` with the path to your workspace. If you are using another backend
than ``local`` you need to adapt the config file to the backend requirements.

Startup
-------

You are now ready to use ``SciXTracer``

.. code-block:: python

    import scixtracer as sx

    dataset = sx.new_dataset("my first dataset")
