StackTaskClient is a command-line and python client for StackTask.

Getting Started
===============

StackTask Client can be installed from PyPI using pip:

::

    pip install python-stacktaskclient

There are a few variants on getting help. A list of global options and supported commands is shown with --help:

::

    stacktask --help

There is also a help command that can be used to get help text for a specific command:

::

    stacktask user-invite --help

Configuration
=============

Authentication using username/password is most commonly used:

::

    export OS_AUTH_URL=<url-to-openstack-identity>
    export OS_PROJECT_NAME=<project-name>
    export OS_USERNAME=<username>
    export OS_PASSWORD=<password>

The corresponding command-line options look very similar:

::

    --os-auth-url <url>
    --os-project-name <project-name>
    --os-username <username>
    [--os-password <password>]
