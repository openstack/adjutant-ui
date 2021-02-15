# Copyright (c) 2016 Catalyst IT Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from adjutant_ui.api import adjutant


class AcknowlegeNotifcation(tables.BatchAction):
    name = 'acknowlege'
    help_text = _("This will acknowlege all selected tasks.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Acknowlege Notification",
            u"Acknowlege Notifications",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Acknowleged Notification",
            u"Acknowleged Notifications",
            count
        )

    def action(self, request, obj_id):
        result = adjutant.notifications_acknowlege(request, obj_id)
        if not result or result.status_code not in [200, 202]:
            exception = exceptions.NotAvailable()
            exception._safe_message = False
            raise exception

    def allowed(self, request, notification=None):
        if notification:
            return not(notification.acknowledged)
        return True


def get_task_link(datum):
    return reverse("horizon:management:tasks:detail",
                   args=(datum.task,))


class ErrorRow(tables.Row):

    def __init__(self, *args, **kwargs):
        super(ErrorRow, self).__init__(*args, **kwargs)
        if not self.datum:
            return
        if self.datum.error:
            self.classes.append('danger')


class NotificationTable(tables.DataTable):
    uuid = tables.Column('uuid', verbose_name=_('Notification ID'),
                         link="horizon:management:notifications:detail")
    task = tables.Column('task', verbose_name=_('Task ID'),
                         link=get_task_link)
    error = tables.Column('error', verbose_name=_('Error'))
    created_on = tables.Column('created_on',
                               verbose_name=_('Created On'))
    notes = tables.Column('notes')

    class Meta(object):
        template = 'notifications/table_override.html'
        name = 'notification_table'
        verbose_name = _('Unacknowledged Notifications')
        table_actions = (AcknowlegeNotifcation, )
        row_actions = (AcknowlegeNotifcation, )
        row_class = ErrorRow
        prev_pagination_param = pagination_param = 'task_page'

    def get_prev_marker(self):
        return str(int(self.page) - 1) if self.data else ''

    def get_marker(self):
        return str(int(self.page) + 1) if self.data else ''

    def get_object_display(self, obj):
        return obj.uuid

    def get_object_id(self, obj):
        return obj.uuid


class AcknowlegedNotificationTable(NotificationTable):

    class Meta(object):
        name = 'acknowleged_table'
        verbose_name = _('Acknowleged Notifications')
        prev_pagination_param = pagination_param = 'acknowledged_page'
        table_actions = ()
