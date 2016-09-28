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


def _authenticated_fetcher(sc):
    """
    A wrapper around the stacktask client object to fetch a template.
    """
    def _do(*args, **kwargs):
        if isinstance(sc.http_client, http.SessionClient):
            method, url = args
            return sc.http_client.request(url, method, **kwargs).content
        else:
            return sc.http_client.raw_request(*args, **kwargs).content

    return _do


# Tasks

@utils.arg('task_id', metavar='<taskid>',
           help=_('Task ID.'))
def do_task_show(sc, args):
    """
    Get individual task.
    """
    try:
        task = sc.tasks.get(task_id=args.task_id)

        formatters = {
            'actions': utils.json_formatter,
            'action_notes': utils.json_formatter,
            'keystone_user': utils.json_formatter,
            'approved_by': utils.json_formatter
        }
        utils.print_dict(task.to_dict(), formatters=formatters)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Task not found: %s') %
                               args.task_id)
    except exc.HTTPBadRequest as e:
        print e.message


@utils.arg('--filters', default={},
           help=_('Filters to use when getting the list.'))
def do_task_list(sc, args):
    """
    Show all tasks in the current project
    """
    fields = [
        'uuid', 'task_type', 'created_on',
        'approved_on', 'completed_on', 'cancelled']
    tasks_list = sc.tasks.list(args.filters)
    utils.print_list(tasks_list, fields)


@utils.arg('task_id', metavar='<taskid>',
           help=_('Task ID.'))
@utils.arg('--data', required=True,
           help=_('New data to update the Task with.'))
def do_task_update(sc, args):
    """
    Update a task with new data and rerun pre-approve validation.
    """
    try:
        resp = sc.tasks.update(args.task_id, args.data)
    except exc.HTTPNotFound as e:
        print e.message
    except exc.HTTPBadRequest as e:
        print e.message
    else:
        print 'Success:', ' '.join(resp.notes)
        do_task_show(sc, args)


@utils.arg('task_id', metavar='<taskid>',
           help=_('Task ID.'))
def do_task_approve(sc, args):
    """
    Approve a task.

    If already approved will rerun post-approve validation
    and reissue/resend token.
    """
    try:
        resp = sc.tasks.approve(args.task_id)
    except exc.HTTPNotFound as e:
        print e.message
    except exc.HTTPBadRequest as e:
        print e.message
    else:
        print 'Success:', ' '.join(resp.notes)
        do_task_show(sc, args)


@utils.arg('task_id', metavar='<taskid>',
           help=_('Task ID.'))
def do_task_reissue_token(sc, args):
    """
    Re-issues the token for the provided pending task.
    """
    try:
        resp = sc.tokens.reissue(task_id=args.task_id)
    except exc.HTTPNotFound as e:
        print e.message
    except exc.HTTPBadRequest as e:
        print e.message
    else:
        print 'Success:', ' '.join(resp.notes)
        do_task_show(sc, args)


@utils.arg('task_id', metavar='<taskid>',
           help=_('Task ID.'))
def do_task_cancel(sc, args):
    """
    Canel the task.
    """
    try:
        resp = sc.tasks.cancel(args.task_id)
    except exc.HTTPNotFound as e:
        print e.message
    except exc.HTTPBadRequest as e:
        print e.message
    else:
        print 'Success: %s' % resp.json()['notes']
        do_task_show(sc, args)


# Notifications

@utils.arg('note_id', metavar='<noteid>',
           help=_('Notification ID.'))
def do_notification_show(sc, args):
    """
    Get individual notification.
    """
    try:
        notification = sc.notifications.get(note_id=args.note_id)

        formatters = {
            'notes': utils.json_formatter
        }
        utils.print_dict(notification.to_dict(), formatters=formatters)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Notification not found: %s') %
                               args.note_id)
    except exc.HTTPBadRequest as e:
        print e.message


@utils.arg('--filters', default={},
           help=_('Filters to use when getting the list.'))
def do_notification_list(sc, args):
    """
    Show all notification.

    This is an admin only endpoint.
    """
    fields = ['uuid', 'task', 'acknowledged', 'created_on']
    notification_list = sc.notifications.list(args.filters)
    utils.print_list(notification_list, fields)


@utils.arg('note_ids', metavar='<noteids>', nargs='+',
           help=_('Notification IDs to acknowledge.'))
def do_notification_acknowledge(sc, args):
    """
    Acknowledge notification.
    """
    try:
        resp = sc.notifications.acknowledge(note_list=args.note_ids)

        print 'Success:', ' '.join(resp.notes)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Notification not found: %s') %
                               args.note_id)
    except exc.HTTPBadRequest as e:
        print e.message


# Tokens

@utils.arg('--filters', default={},
           help=_('Filters to use when getting the list.'))
def do_token_list(sc, args):
    """
    Show all tokens.

    This is an admin only endpoint.
    """
    fields = ['token', 'task', 'created_on', 'expires']
    token_list = sc.tokens.list(args.filters)
    utils.print_list(token_list, fields)


@utils.arg('token', metavar='<token>',
           help=_('Token id of the task'))
def do_token_show(sc, args):
    """
    Show details of this token
    including the arguments required for submit
    """
    try:
        token = sc.tokens.get(args.token)
    except exc.HTTPNotFound as e:
        print e.message
        print "Requested Token was not found."
    else:
        utils.print_dict(token.to_dict())


@utils.arg('token', metavar='<token>',
           help=_('Token id of the task'))
@utils.arg('--password', metavar='<password>', required=True,
           help=_('Password of the new user.'))
def do_token_submit_password(sc, args):
    """
    Submit this token to set or update your password.
    """
    json_data = {'password': args.password}
    _token_submit(sc, args, json_data)


@utils.arg('token', metavar='<token>',
           help=_('Token id of the task'))
@utils.arg('--data', metavar='<data>', required=True,
           help=_('Json with the data to submit.'))
def do_token_submit(sc, args):
    """
    Submit this token to finalise Task.
    """
    try:
        json_data = json.loads(args.data)
    except ValueError as e:
        print e.message
        print "Json data invalid."
        return
    _token_submit(sc, args, json_data)


def _token_submit(sc, args, json_data):
    try:
        sc.tokens.submit(args.token, json_data)
    except exc.HTTPNotFound as e:
        print e.message
        print "Requested token was not found."
    except exc.BadRequest as e:
        print e.message
        print "Bad request. Did you omit a required parameter?"
    else:
        print "Token submitted."


def do_token_clear_expired(sc, args):
    """
    Clear all expired tokens.

    This is an admin only endpoint.
    """
    try:
        resp = sc.tokens.clear_expired()
    except exc.HTTPNotFound as e:
        print e.message
    except exc.HTTPBadRequest as e:
        print e.message
    else:
        print 'Success: %s' % resp.json()['notes']
        fields = ['token', 'task', 'created_on', 'expires']
        token_list = sc.tokens.list({})
        utils.print_list(token_list, fields)


# User

@utils.arg('user_id', metavar='<userid>',
           help=_('User id.'))
def do_user_show(sc, args):
    """
    Show user details.
    """
    try:
        user = sc.users.get(args.user_id)
    except exc.HTTPNotFound as e:
        print e.message
        print "Requested User was not found."
    else:
        utils.print_dict(user.to_dict())


def do_user_list(sc, args):
    """List all users in project"""
    kwargs = {}
    fields = ['id', 'email', 'name', 'roles', 'cohort', 'status']

    project_users = sc.users.list(**kwargs)
    utils.print_list(project_users, fields, sortby_index=1)


@utils.arg('--roles', metavar='<roles>', nargs='+', required=True,
           help=_('Roles to grant to new user'))
@utils.arg('--username', metavar='<username>', default=None,
           help=_('username of user to invite'))
@utils.arg('--email', metavar='<email>', required=True,
           help=_('Email address of user to invite'))
def do_user_invite(sc, args):
    """
    Invites a user to become a member of a project.
    User does not need to have an existing openstack account.
    """
    roles = args.roles or ['Member']

    try:
        sc.users.invite(
            username=args.username, email=args.email, role_list=roles)
    except exc.HTTPNotFound as e:
        print e.message
        print e
    except exc.HTTPBadRequest as e:
        print "400 Bad Request: " + e.message
        print e
    else:
        print "Invitation sent."
        do_user_list(sc, args)


@utils.arg('user_id', metavar='<userid>',
           help=_('User id for unconfirmed user.'))
def do_user_invite_cancel(sc, args):
    """ Cancel user invitation. """
    try:
        resp = sc.users.cancel(args.user_id)
        print 'Success: %s' % resp.json()
    except exc.HTTPNotFound as e:
        print e.message
        print "Requested User was not found."


@utils.arg('--user', '--user-id', metavar='<user>', required=True,
           help=_('Name or ID of user.'))
def do_user_role_list(sc, args):
    """ List the current roles of a user"""
    fields = ['id', 'name']
    user = utils.find_resource(sc.users, args.user)
    kwargs = {'user': user.id}
    roles = sc.user_roles.list(**kwargs)
    utils.print_list(roles, fields, sortby_index=0)


@utils.arg('--user', '--user-id', metavar='<user>', required=True,
           help=_('Name or ID of user.'))
@utils.arg('--role', '--role-id', metavar='<role>', required=True,
           help=_('Name or ID of role.'))
def do_user_role_add(sc, args):
    """Add a role to user"""
    role = utils.find_resource(sc.managed_roles, args.role)
    user = utils.find_resource(sc.users, args.user)
    if sc.user_roles.add(user.id, role=role.name):
        print "Task has been sucessfully completed.\n"
        do_user_list(sc, args)
    else:
        print "Your task was not sucessfully completed."


@utils.arg('--user', '--user-id', metavar='<user>',
           help=_('Name or ID of user.'))
@utils.arg('--role', '--role-id', metavar='<role>', required=True,
           help=_('Name or ID of role.'))
def do_user_role_remove(sc, args):
    """Remove a role from a user"""
    role = utils.find_resource(sc.managed_roles, args.role)
    user = utils.find_resource(sc.users, args.user)
    if sc.user_roles.remove(user.id, role=role.name):
        print "Task has been sucessfully completed.\n"
        do_user_list(sc, args)
    else:
        print "Your task was not sucessfully completed."


@utils.arg('email', metavar='<email>',
           help=_('email of the user account to reset'))
def do_user_password_forgot(sc, args):
    """Request a password reset email for a user."""
    sc.users.password_forgot(args.email)
    print "Task has been sucessfully submitted."
    print "If a user with that email exists, a reset token will be issued."


@utils.arg('email', metavar='<email>',
           help=_('email of the user account to reset'))
def do_user_password_reset(sc, args):
    """Force a password reset for a user. This is an admin only function."""
    sc.users.password_force_reset(args.email)
    print "Task has been sucessfully submitted."
    print "If a user with that email exists, a reset token will be issued."


def do_managed_role_list(sc, args):
    """List roles that may be managed in a given project"""
    fields = ['id', 'name']
    kwargs = {}
    roles = sc.managed_roles.list(**kwargs)
    utils.print_list(roles, fields, sortby_index=1)


# Status

def do_status(sc, args):
    """Requests server status endpoint and returns details of the api server"""
    status = sc.status.get()
    if status.status_code != 200:
        print "Failed: %s" % status.reason
        return
    print json.dumps(
        status.json(), sort_keys=True,
        indent=4, separators=(',', ': '))


# Sign-up
@utils.arg('user', metavar='<user>',
           help=_('User name for new account.'))
@utils.arg('email', metavar='<email>',
           help=_('email of the new account'))
@utils.arg('project_name', metavar='<project_name>',
           help=_('name of the new project'))
def do_sign_up(sc, args):
    """Submits a sign-up from a user requesting a new project and account.

    Note: You can perform an unauthenticated request to this endpoint using
    --os-no-client-auth and --bypass-url <stacktask url>
    """
    status = sc.signup.post(args.user, args.email, args.project_name)
    if status.status_code != 200:
        print "Failed: %s" % status.reason
        return
    print json.dumps(
        status.json(), sort_keys=True,
        indent=4, separators=(',', ': '))
