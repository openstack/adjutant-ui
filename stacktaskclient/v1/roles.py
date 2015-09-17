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
from stacktaskclient.common import utils

import six
from six.moves.urllib import parse

from stacktaskclient.openstack.common.apiclient import base


class Roles(base.Resource):
    def __repr__(self):
        return "<Roles %s>" % self._info

    def create(self, **fields):
        return self.manager.create(self.identifier, **fields)

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self._loaded = True
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.identifier)
        if new:
            self._add_details(new._info)

    @property
    def action(self):
        s = self.stack_status
        # Return everything before the first underscore
        return s[:s.index('_')]

    @property
    def status(self):
        s = self.stack_status
        # Return everything after the first underscore
        return s[s.index('_') + 1:]

    @property
    def identifier(self):
        return '%s/%s' % (self.stack_name, self.id)


class RolesManager(base.BaseManager):
    resource_class = Roles

    def list(self, **kwargs):
        """Get a list of roles that can be managed.

        :param limit: maximum number of stacks to return
        :param marker: begin returning stacks that appear later in the stack
                       list than that represented by this stack id
        :param filters: dict of direct comparison filters that mimics the
                        structure of a stack object
        :rtype: list of :class:`Users`
        """
        params = {}
        #import pdb; pdb.set_trace()
        url = '/roles?%(params)s' % {'params': parse.urlencode(params, True)}
        roles = self._list(url, 'roles')
        for role in roles:
            yield role
