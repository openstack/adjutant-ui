=================
python-stacktaskclient
=================

OpenStack Orchestration API Client Library

This is a client library for Stacktask built on the Catalyst Stacktask API. It
provides a Python API (the ``stacktaskclient`` module) and a command-line tool
(``stacktask``).

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/python-heatclient
* Source: http://git.openstack.org/cgit/openstack/python-heatclient
* Bugs: http://bugs.launchpad.net/python-heatclient

Setup:
python tools/install_venv.py
source .tox/venv/bin/activate
source openrc.sh
stacktask user-tenant-list

'pip list' should give: python-stacktaskclient (0.6.1.dev63, /home/dale/dale/dev/openstack/python-heatclient)
'which stacktask' should give: /home/dale/dale/dev/openstack/python-heatclient/.tox/venv/bin/stacktask
