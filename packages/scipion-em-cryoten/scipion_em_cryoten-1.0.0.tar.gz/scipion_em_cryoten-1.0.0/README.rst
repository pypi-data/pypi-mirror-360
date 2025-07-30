====================
Cryoten  plugin
====================

This plugin provide a wrapper for `Cryoten <https://github.com/jianlin-cheng/cryoten>`_ which efficiently enhances Cryo-EM Density Maps using transformers


Installation
------------

a) Stable version

.. code-block::

    scipion3 installp -p scipion-em-cryoten

b) Developer's version

    * download repository

    .. code-block::

        git clone https://github.com/scipion-em/scipion-em-cryoten.git

    * install

    .. code-block::

        scipion3 installp -p path_to_scipion-em-cryoten --devel

Cryoten will be installed automatically with the plugin using a Conda environment.


Configuration variables
.......................

There are some variables related to the cryoten installation. If you have installed
cryoten within Scipion, you may define `CRYOTEN_ENV_ACTIVATION` for specifying
how to activate the environment. This variable with be used together with the general
conda activation to generate the final cryoten command. For example:

.. code-block::

    CRYOTEN_ENV_ACTIVATION = conda activate cryoten_env

If this variable is not defined, a default value will be provided that will work if the
latest version is installed.

If cryoten is installed already outside Scipion, one could define `MODEL_ANGELO_ACTIVATION`.
This variable will provide an activation (or load) command that can be anything and the Scipion
conda activate will not be prepended. For example (loading cryoten as a module):

.. code-block::

    MODEL_ANGELO_ACTIVATION = module load cryoten/main

If you need to use CUDA different from the one used during Scipion installation (defined by *CUDA_LIB*), you can add *MODEL_ANGELO_CUDA_LIB* variable to the config file.

Protocols
---------

* Model builder

Tests
-----

* scipion3 tests cryoten.tests.tests_cryoten.TestCryoten

