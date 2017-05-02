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
import json

from osc_lib.i18n import _
from osc_lib.command import command


LOG = logging.getLogger(__name__)


def _show_notification(notification_id, client, formatter):
    notification = client.notifications.get(notification_id)
    if formatter == 'table':
        notification._info['notes'] = json.dumps(
            notification.notes, indent=2)
    return zip(*six.iteritems(notification.to_dict()))


class NotificationList(command.Lister):
    """Lists stacktask notifications. """

    def get_parser(self, prog_name):
        parser = super(NotificationList, self).get_parser(prog_name)

        parser.add_argument(
            '--filters', metavar='<filters>',
            required=False,
            help=_('JSON containing filters for the notifications.'),
            default={})

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration

        kwargs = {}
        if parsed_args.filters:
            kwargs['filters'] = parsed_args.filters

        notifications = client.notifications.list(filters=parsed_args.filters)

        headers = ['uuid', 'task', 'acknowledged', 'created_on']

        rows = [[notif.uuid, notif.task, notif.acknowledged,
                 notif.created_on] for notif in notifications]

        return headers, rows


class NotificationShow(command.ShowOne):
    """Show details of one notification."""

    def get_parser(self, prog_name):
        parser = super(NotificationShow, self).get_parser(prog_name)

        parser.add_argument(
            'notification_id', metavar='<notification_id>',
            help=_("The notification ID."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        return _show_notification(parsed_args.notification_id, client,
                                  parsed_args.formatter)


class NotificationAcknowledge(command.Command):
    """ Approve and show details of a notification."""
    def get_parser(self, prog_name):
        parser = super(NotificationAcknowledge, self).get_parser(prog_name)

        parser.add_argument('note_ids', metavar='<noteids>', nargs='+',
                            help=_('Notification IDs to acknowledge.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        resp = client.notifications.acknowledge(note_list=parsed_args.note_ids)
        print('Success', ' '.join(resp.notes))
