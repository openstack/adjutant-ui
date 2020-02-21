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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from adjutant_ui.api import adjutant
from adjutant_ui.api.adjutant import AdjutantApiError
from adjutant_ui.content.notifications import tables as notification_tables


class UnacknowledgedNotificationsTab(tabs.TableTab):
    table_classes = (notification_tables.NotificationTable,)
    template_name = 'horizon/common/_detail_table.html'
    page_title = _("Unacknowledged Notifications")
    name = _('Unacknowledged')
    slug = 'unacknowledged'
    filters = {'acknowledged': {'exact': False}}
    _prev = False
    _more = False
    _page = 1

    def get_notification_table_data(self):
        notifications = []
        self._page = self.request.GET.get(
            self.table_classes[0]._meta.pagination_param, 1)
        try:
            notifications, self._prev, self._more = adjutant.notification_list(
                self.request, filters=self.filters, page=self._page)
        except AdjutantApiError as e:
            if e.message != "Empty Page":
                raise
            try:
                self._page = 1
                notifications, self._prev, self._more = \
                    adjutant.notification_list(
                        self.request, filters=self.filters,
                        page=self._page)
            except Exception:
                exceptions.handle(
                    self.request, _('Failed to list notifications.'))
        except Exception:
            exceptions.handle(self.request, _('Failed to list notifications.'))
        return notifications

    def has_prev_data(self, table):
        table.page = self._page
        return self._prev

    def has_more_data(self, table):
        table.page = self._page
        return self._more


class AcknowlededNotificationsTab(UnacknowledgedNotificationsTab):
    table_classes = (notification_tables.AcknowlegedNotificationTable,)
    page_title = _("Acknowleged Notifications")
    name = _('Acknowleged')
    slug = 'acknowledged'
    filters = {'acknowledged': {'exact': True}}

    def get_acknowleged_table_data(self):
        notifications = []
        self._page = self.request.GET.get(
            self.table_classes[0]._meta.pagination_param, 1)
        try:
            notifications, self._prev, self._more = adjutant.notification_list(
                self.request, filters=self.filters, page=self._page)
        except Exception:
            exceptions.handle(self.request, _('Failed to list notifications.'))
        return notifications


class NotificationTabGroup(tabs.TabGroup):
    slug = "notifications"
    tabs = (UnacknowledgedNotificationsTab, AcknowlededNotificationsTab, )
    sticky = True

    def get_selected_tab(self):
        super(NotificationTabGroup, self).get_selected_tab()
        if not self._selected:
            for tab in self.tabs:
                param = tab.table_classes[0]._meta.pagination_param
                if self.request.GET.get(param):
                    self._selected = self.get_tab(tab.slug)
                    return self._selected
