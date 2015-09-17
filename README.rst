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

===================
Basic setup from source
===================
python tools/install_venv.py
source .tox/venv/bin/activate
source openrc.sh

Verify:
'pip list' should give: python-stacktaskclient (0.6.1.dev63, /home/dale/dale/dev/openstack/python-heatclient)
'which stacktask' should give: /home/dale/dale/dev/openstack/python-heatclient/.tox/venv/bin/stacktask
'stacktask user-tenant-list' should give list of users.

===
Add the registration endpoint
===
Either:
keystone endpoint-create --service registration --publicurl http://192.168.122.160:8040/v1 --internalurl http://192.168.122.160:8040/v1 --region RegionOne
Or:
Add '--bypass-url http://192.168.122.160:8040/v1' to all stacktask calls


===================
Usage examples
===
(NYI) = Not Yet Implemented
(NYI cli) = Not Yet Implemented, client implementation only.
(NYI be)  = Not Yet Implemented, backend service feature required.
===================

List all current users in your tenant:
stacktask user-list

Send/Resend invite for a user to use your tenant:
(NYI cli) stacktask user-invite-send --user-email dale@catalyst-eu.net

List pending invites for members to your tenant:
(NYI be) stacktask user-invite-list

Cancel invite to a user:
(NYI be) stacktask user-invite-cancel --user-email dale@catalyst-eu.net

List pending actions(admin only)
(NYI be) stacktask task-list

Cancel a token(admin only?):
(NYI be) stacktask task-cancel --token-id <token>

Get information about an email token(returns params required, action type):
(NYI cli) stacktask task-get --token-id <token>

Submit an action token(include any parameters):
(NYI cli) stacktask task-submit --token-id <token> --parameters password=123456

Approve a pending action(admin only):
(NYI be) stacktask task-approve --token-id <token>

Allow a user to invite others:
stacktask managed-role-list
(NYI be) stacktask user-role-add --role project_moderator --user dale@catalyst-eu.net

Allow a user to administrate your tenant:
stacktask managed-role-list
(NYI be) stacktask user-role-add --role project_moderator --user dale@catalyst-eu.net
(NYI be) stacktask user-role-add --role project_owner --user dale@catalyst-eu.net

Remove user from your tenant:
stacktask managed-role-list
(NYI be) stacktask user-role-remove --role project_owner --user dale@catalyst-eu.net
(NYI be) stacktask user-role-remove --role project_moderator --user dale@catalyst-eu.net
(NYI be) stacktask user-role-remove --role _member_ --user dale@catalyst-eu.net
(NYI be) stacktask user-role-remove --role Member --user dale@catalyst-eu.net
