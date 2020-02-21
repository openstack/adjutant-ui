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
from adjutant_ui.content.tasks import tables as task_tables


class ActiveTaskListTab(tabs.TableTab):
    table_classes = (task_tables.TaskTable,)
    template_name = 'horizon/common/_detail_table.html'
    page_title = _("Active Tasks")
    name = _('Active')
    slug = 'active'
    filters = {'cancelled': {'exact': False},
               'approved': {'exact': False}}
    _prev = False
    _more = False

    def get_task_table_data(self):
        tasks = []
        marker = self.request.GET.get(
            self.table_classes[0]._meta.pagination_param, 1)
        try:
            tasks, self._prev, self._more = adjutant.task_list(
                self.request, filters=self.filters, page=marker)
        except Exception:
            exceptions.handle(self.request, _('Failed to list tasks.'))
        return tasks

    def has_prev_data(self, table):
        return self._prev

    def has_more_data(self, table):
        return self._more


class ApprovedTaskListTab(ActiveTaskListTab):
    table_classes = (task_tables.ApprovedTaskTable,)
    page_title = _("Approved Tasks")
    name = _('Approved')
    slug = 'approved'
    filters = {'cancelled': {'exact': False},
               'approved': {'exact': True},
               'completed': {'exact': False}}

    def get_approved_table_data(self):
        return super(ApprovedTaskListTab, self).get_task_table_data()


class CompletedTaskListTab(ActiveTaskListTab):
    table_classes = (task_tables.CompletedTaskTable,)
    page_title = _("Completed Tasks")
    name = _('Completed')
    slug = 'completed'
    filters = {'completed': {'exact': True}}

    def get_completed_table_data(self):
        return super(CompletedTaskListTab, self).get_task_table_data()


class CancelledTaskListTab(ActiveTaskListTab):
    table_classes = (task_tables.CancelledTaskTable,)
    name = _('Cancelled')
    slug = 'cancelled'
    filters = {'cancelled': {'exact': True}}

    def get_cancelled_table_data(self):
        return super(CancelledTaskListTab, self).get_task_table_data()


class TaskTabs(tabs.TabGroup):
    slug = "tasks"
    tabs = (ActiveTaskListTab, ApprovedTaskListTab, CompletedTaskListTab,
            CancelledTaskListTab)
    sticky = True

    def get_selected_tab(self):
        super(TaskTabs, self).get_selected_tab()
        if not self._selected:
            for tab in self.tabs:
                param = tab.table_classes[0]._meta.pagination_param
                if self.request.GET.get(param):
                    self._selected = self.get_tab(tab.slug)
                    return self._selected


class TaskOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = 'management/tasks/_task_detail_overview.html'

    def get_context_data(self, request):
        return {"task": self.tab_group.kwargs['task']}


class TaskActionsTab(tabs.Tab):
    name = _("Actions")
    slug = "actions"
    template_name = 'management/tasks/_task_detail_actions.html'

    def get_context_data(self, request):
        return {"task": self.tab_group.kwargs['task']}


class TaskNotesTab(tabs.Tab):
    name = _("Action Notes")
    slug = "notes"
    template_name = 'management/tasks/_task_detail_notes.html'

    def get_context_data(self, request):
        return {"task": self.tab_group.kwargs['task']}


class TaskDetailTabs(tabs.DetailTabsGroup):
    slug = "task_details"
    tabs = (TaskOverviewTab, TaskActionsTab, TaskNotesTab)
