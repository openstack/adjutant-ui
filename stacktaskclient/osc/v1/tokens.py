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
import json
import six

from osc_lib.command import command
from osc_lib.i18n import _

from stacktaskclient import client as stacktask_client

LOG = logging.getLogger(__name__)


def _list_tokens(client, filters={}):
        tokens = client.tokens.list(filters=filters)

        headers = ['Token', 'Task', 'Expires on', 'Created on']
        rows = [[token.token, token.task, token.expires,
                 token.created_on] for token in tokens]

        return headers, rows


class TokenList(command.Lister):
    """Lists stacktask tokens. """

    def get_parser(self, prog_name):
        parser = super(TokenList, self).get_parser(prog_name)

        parser.add_argument(
            '--filters', metavar='<filters>',
            required=False,
            help=_('JSON containing filters for tokens.'),
            default={})

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        return _list_tokens(client, parsed_args.filters)


class TokenShow(command.ShowOne):
    """Show details of one token."""

    def get_parser(self, prog_name):
        parser = super(TokenShow, self).get_parser(prog_name)

        parser.add_argument(
            'token', metavar='<token_id>',
            help=_("The token."))
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
            client = stacktask_client.Client("1", parsed_args.bypass_url)
        token = client.tokens.get(parsed_args.token)
        return zip(*six.iteritems(token.to_dict()))


class TokenSubmit(command.Command):
    """Submit token data."""
    def get_parser(self, prog_name):
        parser = super(TokenSubmit, self).get_parser(prog_name)

        parser.add_argument(
            'token', metavar='<token_id>', help=_('The token.'))
        parser.add_argument(
            'data', metavar='<token_data>',
            help=_('Submission data for the token. Must be valid json.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        resp = client.tokens.submit(
            parsed_args.token, json.loads(parsed_args.data))
        print('Success', ' '.join(resp.notes))


class TokenClear(command.Lister):
    """Clear Expired tokens, admin only."""

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        resp = client.tokens.clear_expired()
        print('Success. ' + ' '.join(resp.json()['notes']))
        return _list_tokens(client)
