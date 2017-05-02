# Copyright (c) 2016 Catalyst IT Ltd.
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
import six

from osc_lib import utils
from osc_lib.command import command
from osc_lib.i18n import _

from stacktaskclient import client as stacktask_client

LOG = logging.getLogger(__name__)


class UserList(command.Lister):
    """Lists users in the currently scoped project. """

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        project_users = client.users.list()
        headers = [
            'id', 'name', 'email', 'roles', 'cohort', 'status']

        rows = [[user.id, user.name, user.email,
                 user.roles, user.cohort, user.status]
                for user in project_users]

        return headers, rows


class UserShow(command.ShowOne):
    """Show details of one user."""

    def get_parser(self, prog_name):
        parser = super(UserShow, self).get_parser(prog_name)

        parser.add_argument(
            'user', metavar='<user>',
            help=_("The user's ID or name."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        # This ends up for names doing multiple requests, it may
        # be better to do something slightly different here
        user_id = utils.find_resource(client.users, parsed_args.user)
        user = client.users.get(user_id)
        return zip(*six.iteritems(user.to_dict()))


class UserInvite(command.Command):
    """
    Invites a user to become a member of a project.
    User does not need to have an existing openstack account.
    """

    def get_parser(self, prog_name):
        parser = super(UserInvite, self).get_parser(prog_name)

        parser.add_argument(
            '--username', metavar='<username>',
            default=None,
            help=_('The username for the new user.'))
        parser.add_argument(
            'email', metavar='<email>',
            help=_('Email address of user to invite'))
        parser.add_argument(
            'roles', metavar='<role>', nargs='+',
            help=_('Roles to give to the user.'))
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.roles:
            parsed_args.roles = ['Member']
        client = self.app.client_manager.registration
        client.users.invite(
            username=parsed_args.username, email=parsed_args.email,
            role_list=parsed_args.roles)
        print("User invited")


class UserInviteCancel(command.Command):
    """ Cancel invite(s) to a project."""
    def get_parser(self, prog_name):
        parser = super(UserInviteCancel, self).get_parser(prog_name)

        parser.add_argument(
            'user', metavar='<user>',
            nargs='+',
            help=_("The user's name or id."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        for user in parsed_args.user:
            user_id = utils.find_resource(client.users, user)
            client.users.cancel(user_id=user_id)
        print("Invite(s) Cancelled")


class UserRoleAdd(command.Command):
    """ Add a role to a user."""
    def get_parser(self, prog_name):
        parser = super(UserRoleAdd, self).get_parser(prog_name)

        parser.add_argument(
            'user', metavar='<user>',
            help=_("The user's name or id.."))
        parser.add_argument(
            'role', metavar='<role>',
            help=_("The role's name or id."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration

        role = utils.find_resource(client.managed_roles, parsed_args.role)
        user = utils.find_resource(client.users, parsed_args.user)
        if client.user_roles.add(user.id, role=role.name):
            print(_("Role added"))


class UserRoleRemove(command.Command):
    """ Remove a role from a user."""
    def get_parser(self, prog_name):
        parser = super(UserRoleRemove, self).get_parser(prog_name)

        parser.add_argument(
            'user', metavar='<user>',
            help=_("The user's name or id.."))
        parser.add_argument(
            'role', metavar='<user>',
            help=_("The role's name or id."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        role = utils.find_resource(client.managed_roles, parsed_args.role)
        user = utils.find_resource(client.users, parsed_args.user)

        if client.user_roles.remove(user.id, role=role.name):
            print(_("Role removed"))


class UserRoleList(command.Lister):
    """Lists the roles a user has on a project"""
    def get_parser(self, prog_name):
        parser = super(UserRoleList, self).get_parser(prog_name)

        parser.add_argument(
            'user', metavar='<user>',
            help=_("Name or ID of user."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration

        user = utils.find_resource(client.users, parsed_args.user)
        kwargs = {'user': user.id}
        roles = [[role.id, role.name] for role
                 in client.user_roles.list(**kwargs)]
        return ['id', 'name'], roles


class ManageableRolesList(command.Lister):
    """ Lists roles able to be managed by the current user """
    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        roles = client.managed_roles.list()

        headers = ['id', 'name']
        rows = [[role.id, role.name] for role in roles]
        return headers, rows


class PasswordReset(command.Command):
    """ Force password reset for a user, admin only. """

    def get_parser(self, prog_name):
        parser = super(PasswordReset, self).get_parser(prog_name)

        parser.add_argument(
            'email', metavar='<email>',
            help=_("Email address of the user."))
        parser.add_argument(
            '--username', metavar='<username>', default=None,
            help=_('Username of the account to reset if the username '
                   'is different than the email'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration

        data = {'email': parsed_args.email}
        if parsed_args.username:
            data['username'] = parsed_args.username

        client.users.password_force_reset(data)
        print("Task has been sucessfully submitted.")
        print("If a user with that email exists, a reset "
              "token will be issued.")


class PasswordForgot(command.Command):
    """ Links to user forgotten password endpoint, does not require auth."""
    auth_required = False

    def get_parser(self, prog_name):
        parser = super(PasswordForgot, self).get_parser(prog_name)

        parser.add_argument(
            'email', metavar='<email>',
            help=_("Email address of the user."))
        parser.add_argument(
            '--username', metavar='<username>', default=None,
            help=_('Username of the account to reset if the username '
                   'is different than the email'))
        parser.add_argument(
            '--bypass-url', metavar='<bypass-url>', default=None,
            help=_('Bypasss URL for unauthenticated access to the endpoint.'))
        return parser

    def take_action(self, parsed_args):
        if not parsed_args.bypass_url:
            self.app.client_manager._auth_required = True
            self.app.client_manager.setup_auth()
            client = self.app.client_manager.registration
        else:
            client = stacktask_client.Client(1, parsed_args.bypass_url)

        client.users.password_forgot(parsed_args.email, parsed_args.username)
        print("Task has been sucessfully submitted.")
        print("If a user with that email exists, a reset "
              "token will be issued.")
