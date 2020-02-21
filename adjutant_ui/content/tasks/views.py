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
from horizon import forms
from horizon import tabs

from horizon.utils import memoized

from adjutant_ui.api import adjutant
from adjutant_ui.content.tasks import forms as task_forms
from adjutant_ui.content.tasks import tables as task_tables
from adjutant_ui.content.tasks import tabs as task_tabs

import json


class IndexView(tabs.TabbedTableView):
    tab_group_class = task_tabs.TaskTabs
    template_name = 'management/tasks/index.html'
    redirect_url = 'horizon:management:tasks:index'
    page_title = _("Admin Tasks")


class TaskDetailView(tabs.TabView):
    tab_group_class = task_tabs.TaskDetailTabs
    template_name = 'horizon/common/_detail.html'
    redirect_url = 'horizon:management:tasks:index'
    page_title = "{{ task.task_type }}"

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        task = self.get_data()
        context["task"] = task
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(
            adjutant.task_obj_get(self.request, task=task))
        return context

    def _get_actions(self, task):
        if task.status == 'Approved; Incomplete':
            table = task_tables.ApprovedTaskTable(self.request)
        else:
            table = task_tables.TaskTable(self.request)
        return table.render_row_actions(task)

    @memoized.memoized_method
    def get_data(self):
        return adjutant.task_get(self.request, self.kwargs['task_id']).json()

    def get_tabs(self, request, *args, **kwargs):
        task = self.get_data()
        return self.tab_group_class(request, task=task, **kwargs)


class UpdateTaskView(forms.ModalFormView):
    form_class = task_forms.UpdateTaskForm
    form_id = "update_user_form"
    modal_header = _("Update Task")
    submit_label = _("Update")
    submit_url = 'horizon:management:tasks:update'
    template_name = 'management/tasks/update.html'
    context_object_name = 'project_users'
    success_url = "horizon:management:tasks:detail"
    page_title = _("Update Task")

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['task_id'],))

    @memoized.memoized_method
    def get_object(self):
        try:
            return adjutant.task_get(self.request,
                                     self.kwargs['task_id']).json()
        except Exception:
            msg = _('Unable to retrieve user.')
            url = reverse('horizon:management:tasks:index')
            exceptions.handle(self.request, msg, redirect=url)

    def get_context_data(self, **kwargs):
        context = super(UpdateTaskView, self).get_context_data(**kwargs)
        context['task'] = self.get_object()
        args = (self.kwargs['task_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        task = self.get_object()
        task_data = {}
        for data in [action['data'] for action in task['actions']]:
            task_data.update(data)
        data = {'task_id': self.kwargs['task_id'],
                'task_type': task['task_type'],
                'task_data': json.dumps(task_data, indent=4),
                }
        return data
