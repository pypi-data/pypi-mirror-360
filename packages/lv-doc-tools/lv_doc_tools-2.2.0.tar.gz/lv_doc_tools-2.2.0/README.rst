.. Thes  are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/lv_doc_tools.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/lv_doc_tools
    .. image:: https://readthedocs.org/projects/lv_doc_tools/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://lv_doc_tools.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/lv_doc_tools/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/lv_doc_tools
    .. image:: https://img.shields.io/pypi/v/lv_doc_tools.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/lv_doc_tools/
    .. image:: https://img.shields.io/conda/vn/conda-forge/lv_doc_tools.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/lv_doc_tools
    .. image:: https://pepy.tech/badge/lv_doc_tools/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/lv_doc_tools
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/lv_doc_tools

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

============
lv_doc_tools
============


	Tools for streamlining doucmentation of LabView projects

This module provides a wrapper for the antidoc, ascii-doctor and caraya test tools. It is aimed at simple CLI interface and incorporation to CD pipelines. The configuration is via a single json file.


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.


Installation
============

Depending on your platform, you may need to install additional dependencies for `asciidoctor`:

- **Windows**: Install `asciidoctor-pdf` using the following command:

  .. code-block:: bash

      pip install lv_doc_tools

Alternatively, you can install `asciidoctor` manually on Windowss by following these steps or using the link(https://docs.asciidoctor.org/asciidoctor/latest/install/windows/):
1. Install Ruby from the official website: https://rubyinstaller.org/downloads/
2. Verify that Ruby is installed correctly by running `ruby -v` in the command prompt.
3. Install the Asciidoctor gem by running the following command in the command prompt:

  .. code-block:: bash

      gem install asciidoctor-pdf


Usage
=====

Once installed, you can use the CLI tool `lv_doc_tool` to generate documentation. For example:

.. code-block:: bash

    lv_doc_tool config.json

This will read the `config.json` file and generate the documentation based on the configuration.

Help
====

To see the available options for the CLI tool, run:

.. code-block:: bash

    lv_doc_tool --help
