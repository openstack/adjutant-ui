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

from stacktaskclient.openstack.common.apiclient import base


class Task(base.Resource):
    pass


class TaskManager(base.ManagerWithFind):
    resource_class = Task

    def get(self, user):
        return self._get("/tasks/%s" % base.getid(user))

    def list(self, **kwargs):
        """Get a list of tasks.

        :rtype: list of :class:`Task`
        """

        params = {}
        url = '/tasks?%(params)s' % {
            'params': parse.urlencode(params, True)
        }
        return self._list(url, 'tasks')
