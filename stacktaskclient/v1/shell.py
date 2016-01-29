# Copyright (C) 2016 Catalyst IT Ltd
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

import json
from stacktaskclient.common import utils
from stacktaskclient.common import http

from stacktaskclient.openstack.common._i18n import _

import stacktaskclient.exc as exc

logger = logging.getLogger(__name__)


def _authenticated_fetcher(hc):
    """A wrapper around the stacktask client object to fetch a template.
    """
    def _do(*args, **kwargs):
        if isinstance(hc.http_client, http.SessionClient):
            method, url = args
            return hc.http_client.request(url, method, **kwargs).content
        else:
            return hc.http_client.raw_request(*args, **kwargs).content

    return _do


# @utils.arg('--tenant-id', metavar='<tenant>',
#            help=_('Specify a particular tenant'))
def do_user_list(hc, args):
    """List all users in tenant"""
    kwargs = {}
    fields = ['id', 'email', 'name', 'roles', 'status']

    tenant_users = hc.users.list(**kwargs)
    utils.print_list(tenant_users, fields, sortby_index=1)


@utils.arg('--roles', metavar='<roles>', nargs='+',
           help=_('Roles to grant to new user'))
@utils.arg('--tenant', '--tenant-id', metavar='<tenant>',
           help=_('Invite to a particular tenant id'))
@utils.arg('email', metavar='<email>',
           help=_('Email address of user to invite'))
def do_user_invite(hc, args):
    """
      Invites a user to become a member of a tenant.
      User does not need to have an existing openstack account.
    """
    roles = args.roles or ['Member']

    if args.tenant:
        # utils.find_resource(hc.tenants, args.tenant).id
        tenant_id = args.tenant
    else:
        tenant_id = None

    try:
        hc.users.invite(email=args.email, tenant_id=tenant_id, role_list=roles)
    except exc.HTTPNotFound as e:
        print e.message
        print e
    except exc.HTTPBadRequest as e:
        print "400 Bad Request: " + e.message
        print e
    else:
        print "Invitation sent. (todo: print only pending users)"
        do_user_list(hc, args)


@utils.arg('--all-tenants',
           help=_('Display tasks from all tenants instead of just current'))
def do_task_list(hc, args):
    """
    Show all pending tasks in the current tenant
    """
    fields = [
        'uuid', 'task_type', 'created_on',
        'approved_on', 'completed_on', 'actions', 'action_notes']
    tasks_list = hc.tasks.list()
    # split by type, and print with different fields
    # task_types = {}
    # for task in task_types:
    #    task_types[task.task_type] = task
    utils.print_list(tasks_list, fields)


@utils.arg('--task-id', metavar='<taskid>', required=True,
           help=_('Task ID.'))
def do_task_reissue_token(hc, args):
    """
        Re-issues the token for the provided pending task.
    """
    try:
        resp = hc.tokens.reissue(task_id=args.task_id)
    except exc.HTTPNotFound as e:
        print e.message
    except exc.HTTPBadRequest as e:
        print e.message
    else:
        print 'Success:', ' '.join(resp.notes)
        do_user_list(hc, args)


@utils.arg('token', metavar='<token>',
           help=_('Token id of the task'))
def do_token_show(hc, args):
    """
        Show details of this token
        including the arguments required for submit
    """
    fields = ['required_fields', 'actions']
    try:
        tokens = hc.tokens.show(args.token)
    except exc.HTTPNotFound as e:
        print e.message
        print "Requested token was not found."
    else:
        utils.print_list(tokens, fields, sortby_index=1)


@utils.arg('token', metavar='<token>',
           help=_('Token id of the task'))
@utils.arg('--password', metavar='<password>', required=True,
           help=_('Password of the new user.'))
def do_token_submit(hc, args):
    """
       Submit this token to allow processing of this task.
       Currently only supports NewUser action, which requires a password
    """
    print("do_token_submit")
    kwargs = {'password': args.password}
    try:
        hc.tokens.submit(args.token, kwargs)
    except exc.HTTPNotFound as e:
        print e.message
        print "Requested token was not found."
    except exc.BadRequest as e:
        print e.message
        print "Bad request. Did you omit a required parameter?"
    else:
        print "Token submitted."


@utils.arg('--user', '--user-id', metavar='<user>', required=True,
           help=_('Name or ID of user.'))
def do_user_role_list(hc, args):
    """ List the current roles of a user"""
    fields = ['id', 'name']
    user = utils.find_resource(hc.users, args.user)
    kwargs = {'user': user.id}
    roles = hc.user_roles.list(**kwargs)
    utils.print_list(roles, fields, sortby_index=0)


@utils.arg('--user', '--user-id', metavar='<user>', required=True,
           help=_('Name or ID of user.'))
@utils.arg('--role', '--role-id', metavar='<role>', required=True,
           help=_('Name or ID of role.'))
@utils.arg('--tenant', '--tenant-id', metavar='<tenant>',
           help=_('Name or ID of tenant.'))
def do_user_role_add(hc, args):
    """Add a role to user"""
    user = utils.find_resource(hc.users, args.user)
    role = utils.find_resource(hc.managed_roles, args.role)
    if hc.user_roles.add(user.id, role.name):
        do_user_role_list(hc, args)


@utils.arg('--user', '--user-id', metavar='<user>',
           help=_('Name or ID of user.'))
@utils.arg('--role', '--role-id', metavar='<role>', required=True,
           help=_('Name or ID of role.'))
@utils.arg('--tenant', '--tenant-id', metavar='<tenant>',
           help=_('Name or ID of tenant.'))
def do_user_role_remove(hc, args):
    """Remove a role from a user"""
    user = utils.find_resource(hc.users, args.user)
    role = utils.find_resource(hc.managed_roles, args.role)
    if hc.user_roles.remove(user.id, role.name):
        do_user_role_list(hc, args)


@utils.arg('email', metavar='<email>',
           help=_('email of the user account to reset'))
def do_user_password_forgot(rc, args):
    """Request a password reset email for a user."""
    data = {"email": args.email}
    status = rc.http_client.post("/openstack/forgotpassword/", data=data)
    if status.status_code != 200:
        print "Failed: %s" % status.reason
        return


@utils.arg('email', metavar='<email>',
           help=_('email of the user account to reset'))
def do_user_password_reset(rc, args):
    """Force a password reset for a user. This is an admin only function."""
    print "NOT YET IMPLEMENTED."
    pass


# @utils.arg('--user', '--user-id', metavar='<user>', required=True,
#            help=_('Name or ID of user.'))
# @utils.arg('--roles', '--role-id', metavar='<roles>', required=True,
#            help=_('List of role ids'))
# @utils.arg('--tenant', '--tenant-id', metavar='<tenant>',
#            help=_('Name or ID of tenant.'))
# def do_user_role_set(hc, args):
#     """Set the roles of a user. May be empty"""
#     print("do_user_role_set")
#     pass


@utils.arg('--tenant', metavar='<tenant>',
           help=_('Name or ID of tenant.'))
def do_managed_role_list(rc, args):
    """List roles that may be managed in a given tenant"""
    fields = ['id', 'name']
    kwargs = {}
    roles = rc.managed_roles.list(**kwargs)
    utils.print_list(roles, fields, sortby_index=1)


def do_status(rc, args):
    """Requests server status endpoint and returns details of the api server"""
    status = rc.http_client.get("/status")
    if status.status_code != 200:
        print "Failed: %s" % status.reason
        return
    print json.dumps(
        json.loads(status.content), sort_keys=True,
        indent=4, separators=(',', ': '))
