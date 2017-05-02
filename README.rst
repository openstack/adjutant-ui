StackTaskClient is a command-line and python client for StackTask.

Getting Started
===============

StackTask Client can be installed from PyPI using pip:

::

    pip install python-openstackclient python-stacktaskclient


The command line client is installed as a plugin for the OpenStack client, and
an older deprecated version is available under the entry point 'stacktask'.

Python API
==========

In order to use the python api directly, you must first obtain an auth
token and identify which endpoint you wish to speak to::

  >>> stacktask_url = 'http://stacktask.example.org:8004/v1/'
  >>> auth_token = '3bcc3d3a03f44e3d8377f9247b0ad155'

Once you have done so, you can use the API like so::

  >>> from stacktaskclient.client import Client
  >>> stacktask = Client('1', endpoint=stacktask_url, token=auth_token)

An auth token isn't needed for accessing signup, user.password_forgot(),
token.submit() or token.get().
