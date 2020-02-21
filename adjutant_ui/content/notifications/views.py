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

from horizon import exceptions
from horizon import tabs
from horizon import views

from horizon.utils import memoized

from adjutant_ui.api import adjutant
from adjutant_ui.content.notifications import tables as notification_tables
from adjutant_ui.content.notifications import tabs as notification_tab


class IndexView(tabs.TabbedTableView):
    tab_group_class = notification_tab.NotificationTabGroup
    template_name = 'notifications/index.html'
    redirect_url = 'horizon:management:notifications:index'
    page_title = _("Admin Notifications")


class NotificationDetailView(views.HorizonTemplateView):
    redirect_url = "horizon:management:notifications:index"
    template_name = 'notifications/detail.html'
    page_title = "Notification: {{ notification.uuid }}"

    def get_context_data(self, **kwargs):
        context = super(NotificationDetailView, self).get_context_data(
            **kwargs)
        notification, task = self.get_data()
        context["notification"] = notification
        context['task'] = task
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(notification=notification)
        return context

    def _get_actions(self, notification):
        table = notification_tables.NotificationTable(self.request)
        return table.render_row_actions(notification)

    @memoized.memoized_method
    def get_data(self):
        try:
            notification = adjutant.notification_obj_get(
                self.request, self.kwargs['notif_id'])
            task = adjutant.task_obj_get(self.request,
                                         task_id=notification.task)
            return notification, task
        except Exception:
            msg = _('Unable to retrieve notification.')
            url = reverse('horizon:management:notifications:index')
            exceptions.handle(self.request, msg, redirect=url)
