============
MCH OSS Demo
============

Python library to demonstrate the MeteoSwiss open-source template.




Development Setup with Poetry
-----------------------------

Building the Project
''''''''''''''''''''
.. code-block:: console

    $ cd mch-oss-demo
    $ poetry install

Run Tests
'''''''''

.. code-block:: console

    $ poetry run pytest

Run Quality Tools
'''''''''''''''''

.. code-block:: console

    $ poetry run pylint mch_oss_demo
    $ poetry run mypy mch_oss_demo

Generate Documentation
''''''''''''''''''''''

.. code-block:: console

    $ poetry run sphinx-build doc doc/_build

Then open the index.html file generated in *mch-oss-demo/doc/_build/*.

Build wheels
''''''''''''

.. code-block:: console

    $ poetry build

Using the Library
-----------------

To install mch-oss-demo in your project, run this command in your terminal:

.. code-block:: console

    $ poetry add mch-oss-demo

You can then use the library in your project through

    import mch_oss_demo
