# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
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

import fnmatch
import logging

from oslo_serialization import jsonutils
from oslo_utils import strutils
import six
from six.moves.urllib import request
import time
import yaml

from stacktaskclient.common import deployment_utils
from stacktaskclient.common import event_utils
from stacktaskclient.common import http
from stacktaskclient.common import template_format
from stacktaskclient.common import template_utils
from stacktaskclient.common import utils

from stacktaskclient.openstack.common._i18n import _
from stacktaskclient.openstack.common._i18n import _LE
from stacktaskclient.openstack.common._i18n import _LW

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


def do_user_tenant_list(hc, args):
    """List all users in tenant"""
    kwargs = {}
    fields = ['id', 'username', 'email', 'roles']

    tenant_users = hc.users.list(**kwargs)
    utils.print_list(tenant_users, fields, sortby_index=1)


@utils.arg('--tenant-id', metavar='<tenant>',
           help=_('Invite to a particular tenant'))
@utils.arg('--user-email', metavar='<email>',
           help=_('Email address of user to invite'))
def do_user_tenant_invite(hc, args):
    """
      Invites a user to become a member of a tenant.
      User does not need to have an existing openstack account.
    """
    print("do_user_tenant_invite")
    pass


@utils.arg('--user', '--user-id', metavar='<user>',
           help=_('Name or ID of user.'))
@utils.arg('--tenant', '--tenant-id', metavar='<tenant>',
           help=_('Name or ID of tenant.'))
def do_user_role_add(hc, args):
    """Add a role to user"""
    print("do_user_role_add")
    pass


@utils.arg('--user', '--user-id', metavar='<user>',
           help=_('Name or ID of user.'))
@utils.arg('--tenant', '--tenant-id', metavar='<tenant>',
           help=_('Name or ID of tenant.'))
#@utils.arg('--role', keystone )
def do_user_role_remove(hc, args):
    """Remove a role from a user"""
    print("do_user_role_remove")
    pass


@utils.arg('--tenant', metavar='<tenant>',
           help=_('Name or ID of tenant.'))
def do_managed_role_list(rc, args):
    """List roles that may be managed in a given tenant"""
    fields = ['id', 'name']
    kwargs = {}
    #import pdb; pdb.set_trace()
    roles = rc.roles.list(**kwargs)
    utils.print_list(roles, fields, sortby_index=1)


#----- ------------ OLD HEAT SHELL COMMANDS -------------------


@utils.arg('-s', '--show-deleted', default=False, action="store_true",
           help=_('Include soft-deleted stacks in the stack listing.'))
@utils.arg('-n', '--show-nested', default=False, action="store_true",
           help=_('Include nested stacks in the stack listing.'))
@utils.arg('-a', '--show-hidden', default=False, action="store_true",
           help=_('Include hidden stacks in the stack listing.'))
@utils.arg('-f', '--filters', metavar='<KEY1=VALUE1;KEY2=VALUE2...>',
           help=_('Filter parameters to apply on returned stacks. '
           'This can be specified multiple times, or once with parameters '
           'separated by a semicolon.'),
           action='append')
@utils.arg('-t', '--tags', metavar='<TAG1,TAG2...>',
           help=_('Show stacks containing these tags, combine multiple tags '
                  'using the boolean AND expression'))
@utils.arg('--tags-any', metavar='<TAG1,TAG2...>',
           help=_('Show stacks containing these tags, combine multiple tags '
                  'using the boolean OR expression'))
@utils.arg('--not-tags', metavar='<TAG1,TAG2...>',
           help=_('Show stacks not containing these tags, combine multiple '
                  'tags using the boolean AND expression'))
@utils.arg('--not-tags-any', metavar='<TAG1,TAG2...>',
           help=_('Show stacks not containing these tags, combine multiple '
                  'tags using the boolean OR expression'))
@utils.arg('-l', '--limit', metavar='<LIMIT>',
           help=_('Limit the number of stacks returned.'))
@utils.arg('-m', '--marker', metavar='<ID>',
           help=_('Only return stacks that appear after the given stack ID.'))
@utils.arg('-g', '--global-tenant', action='store_true', default=False,
           help=_('Display stacks from all tenants. Operation only authorized '
                  'for users who match the policy in heat\'s policy.json.'))
@utils.arg('-o', '--show-owner', action='store_true', default=False,
           help=_('Display stack owner information. This is automatically '
                  'enabled when using %(arg)s.') % {'arg': '--global-tenant'})
def do_stack_list(hc, args=None):
    '''List the user's stacks.'''
    kwargs = {}
    fields = ['id', 'username', 'email', 'roles']
    if args:
        kwargs = {'limit': args.limit,
                  'marker': args.marker,
                  'filters': utils.format_parameters(args.filters),
                  'tags': args.tags,
                  'tags_any': args.tags_any,
                  'not_tags': args.not_tags,
                  'not_tags_any': args.not_tags_any,
                  'global_tenant': args.global_tenant,
                  'show_deleted': args.show_deleted,
                  'show_hidden': args.show_hidden}
        if args.show_nested:
            fields.append('parent')
            kwargs['show_nested'] = True

        if args.global_tenant or args.show_owner:
            fields.insert(2, 'stack_owner')
        if args.global_tenant:
            fields.insert(2, 'project')

    stacks = hc.stacks.list(**kwargs)
    utils.print_list(stacks, fields, sortby_index=3)
