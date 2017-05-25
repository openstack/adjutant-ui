# Copyright 2014 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_OS_REGISTRATION_VERSION = '1'
DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_registration_version'
API_NAME = "registration"
API_VERSIONS = {
    "1": "adjutantclient.v1.client.Client",
}


def make_client(instance):
    """Returns an adjutant service client."""
    version = instance._api_version[API_NAME]
    try:
        version = int(version)
    except ValueError:
        version = float(version)

    version = 1

    adjutant_client = utils.get_client_class(
        API_NAME,
        version,
        API_VERSIONS)

    LOG.debug('Instantiating adjutant client: %s', adjutant_client)

    kwargs = {'region_name': instance.region_name}

    if instance.session:
        kwargs.update({'session': instance.session,
                       'service_type': API_NAME})
    else:
        endpoint = instance.get_endpoint_for_service_type(
            API_NAME,
            region_name=instance.region_name,
            interface=instance.interface,
        )

        kwargs.update({'endpoint': endpoint,
                       'auth_url': instance.auth.auth_url,
                       'username': instance.auth_ref.username,
                       'token': instance.auth_ref.auth_token})

    client = adjutant_client(**kwargs)

    return client


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-registration-version',
        metavar='<registration-version>',
        default=utils.env(
            'OS_REGISTRATION_VERSION',
            default=DEFAULT_OS_REGISTRATION_VERSION),
        help=('Client version, default=' +
              DEFAULT_OS_REGISTRATION_VERSION +
              ' (Env: DEFAULT_OS_REGISTRATION_VERSION)'))
    return parser
