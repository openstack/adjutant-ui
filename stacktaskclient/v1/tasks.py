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

    def get(self, task_id):
        return self._get("/tasks/%s" % base.getid(task_id))

    def list(self, **kwargs):
        """Get a list of tasks.

        :rtype: list of :class:`Task`
        """
        url = '/tasks?%(params)s' % {
            'params': parse.urlencode(kwargs, True)
        }
        return self._list(url, 'tasks')

    def update(self, task_id, data):
        """
        Update a task with new data and rerun pre-approve validation.
        """
        url = 'tasks/%s' % task_id
        return self._put(url, data)

    def approve(self, task_id):
        """
        Approve a task.

        If already approved will rerun post-approve validation
        and reissue/resend token.
        """
        data = {'approved': True}
        url = 'tasks/%s' % task_id
        return self._post(url, data)

    def cancel(self, task_id):
        """
        Cancel a task.
        """
        url = 'tasks/%s' % task_id
        return self._delete(url)
