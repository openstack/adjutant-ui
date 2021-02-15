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

from horizon import forms
from horizon import messages

import json

from adjutant_ui.api import adjutant


class UpdateTaskForm(forms.SelfHandlingForm):
    task_id = forms.CharField(widget=forms.HiddenInput())
    task_type = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': True}))
    task_data = forms.CharField(widget=forms.Textarea)

    def clean_task_data(self):
        taskdata = self.cleaned_data['task_data']
        try:
            json.loads(taskdata)
        except ValueError:
            raise forms.ValidationError(
                "Invalid non-JSON data in Task Data field")

        return taskdata

    def handle(self, request, data):
        task_id = self.cleaned_data.pop('task_id')
        try:
            response = adjutant.task_update(
                request, task_id, data['task_data'])
            if response.status_code in [200, 202]:
                messages.success(request, _('Updated task successfully.'))
            elif response.status_code == 400:
                messages.error(request, _(response.text))
            else:
                messages.error(request, _('Failed to update task.'))
            return True
        except Exception:
            messages.error(request, _('Failed to update task.'))
            return False
