AdjutantClient is a command-line and python client for Adjutant.

Getting Started
===============

Adjutant Client can be installed from PyPI using pip:

::

    pip install python-openstackclient python-adjutantclient


The command line client is installed as a plugin for the OpenStack client, and
an older deprecated version is available under the entry point 'adjutant'.

Python API
==========

In order to use the python api directly, you must first obtain an auth
token and identify which endpoint you wish to speak to::

  >>> adjutant_url = 'http://adjutant.example.org:8004/v1/'
  >>> auth_token = '3bcc3d3a03f44e3d8377f9247b0ad155'

Once you have done so, you can use the API like so::

  >>> from adjutantclient.client import Client
  >>> adjutant = Client('1', endpoint=adjutant_url, token=auth_token)

An auth token isn't needed for accessing signup, user.password_forgot(),
token.submit() or token.get().
