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

from six.moves.urllib import parse

from adjutantclient.common import base
from adjutantclient import exc


class Role(base.Resource):
    pass


class ManagableRole(base.Resource):
    pass


class ManagedRoleManager(base.ManagerWithFind):
    resource_class = ManagableRole

    def list(self, **kwargs):
        """Get a list of roles that can be managed.

        :rtype: list of :class:`Role`
        """
        params = {}
        url = '/openstack/roles?%(params)s' % {
            'params': parse.urlencode(params, True)
        }
        return self._list(url, 'roles')

    def get(self, role_id):
        """
        Get a role by role_id
        """
        # Right now the only way is to list them all, then iterate.
        # Perhaps a filter or new endpoint would be useful here.
        roles = self.list()
        for role in roles:
            if role.id == role_id:
                return role
        raise exc.HTTPNotFound()


class UserRoleManager(base.BaseManager):
    resource_class = Role

    def list(self, **kwargs):
        """List roles for a given user"""
        # TODO: Look up user by name/id
        url = '/openstack/users/%s/roles' % kwargs['user']
        return self._list(url, 'roles')

    def add(self, user, role=None, roles=None):
        """Add a role to a user"""
        # TODO: resolve the roles and users into id's
        # user_id = base.getid(user)
        user_id = user
        # role_id = role
        if role:
            params = {
                'roles': [role]
            }
        elif roles:
            params = {
                'roles': roles
            }

        route = '/openstack/users/%s/roles'
        url = route % (user_id)
        try:
            self._put(url, json=params, response_key=None)
        except exc.HTTPBadRequest as e:
            print e.message
            return False

        return True

    def remove(self, user_id, role=None, roles=None):
        """Remove a role or roles from a user"""
        if role:
            params = {
                'roles': [role]
            }
        elif roles:
            params = {
                'roles': roles
            }

        route = '/openstack/users/%s/roles'
        url = route % (user_id)
        try:
            self._delete(url, json=params, response_key=None)
        except exc.HTTPBadRequest as e:
            print e.message
            return False

        return True
