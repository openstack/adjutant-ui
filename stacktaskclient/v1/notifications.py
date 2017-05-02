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


class Notification(base.Resource):
    pass


class NotificationManager(base.ManagerWithFind):
    resource_class = Notification

    def get(self, note_id):
        return self._get("/notifications/%s" % base.getid(note_id))

    def list(self, **kwargs):
        """Get a list of notifications.

        :rtype: list of :class:`Notification`
        """
        url = '/notifications?%(params)s' % {
            'params': parse.urlencode(kwargs, True)
        }
        return self._list(url, 'notifications')

    def acknowledge(self, note_id=None, note_list=[]):
        """
        Acknowledge a single notification or many.
        """
        if note_id:
            data = {'acknowledged': True}
            url = 'notifications/%s' % note_id
            return self._post(url, data)
        elif note_list:
            data = {'notifications': note_list}
            return self._post('notifications', data)
