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

from osc_lib.command import command
from osc_lib.i18n import _

from adjutantclient import client as adjutant_client


LOG = logging.getLogger(__name__)


class Signup(command.Command):
    """Submits a sign-up request."""
    auth_required = False

    def get_parser(self, prog_name):
        parser = super(Signup, self).get_parser(prog_name)

        parser.add_argument(
            '--user', metavar='<user>',
            required=False,
            help=_('Username for new account. '
                   'May not be required depending on API configuration.'),
            default=None)
        parser.add_argument(
            'email', metavar='<email>',
            help=_('New account email address.'))
        parser.add_argument(
            'project_name', metavar='<project_name>',
            help=_('Name of the new project'))
        parser.add_argument(
            '--bypass-url', metavar='<bypass-url>', default=None,
            help=_('Bypasss URL for unauthenticated access to the endpoint.'))
        parser.add_argument(
            '--setup-network', action='store_true',
            help=_('Create a default network during project creation.'))

        return parser

    def take_action(self, parsed_args):
        if not parsed_args.bypass_url:
            # NOTE(amelia): Assumes that this is an already authenticated
            # user wanting to access and submit a sign up (I.E. an admin)
            self.app.client_manager._auth_required = True
            self.app.client_manager.setup_auth()
            client = self.app.client_manager.registration
        else:
            client = adjutant_client.Client(1, parsed_args.bypass_url)

        signup = client.signup.post(parsed_args.user, parsed_args.email,
                                    parsed_args.project_name,
                                    parsed_args.setup_network).json()
        print(json.dumps(signup, indent=2))
