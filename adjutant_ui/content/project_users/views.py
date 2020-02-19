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
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from adjutant_ui.content.project_users import tables as users_tables

from adjutant_ui.content.project_users import forms as users_forms

from adjutant_ui.api import adjutant


class InviteUserView(forms.ModalFormView):
    form_class = users_forms.InviteUserForm
    form_id = "invite_user_form"
    modal_header = _("Invite User")
    submit_label = _("Invite User")
    submit_url = reverse_lazy('horizon:management:project_users:invite')
    template_name = 'management/project_users/invite.html'
    context_object_name = 'project_users'
    success_url = reverse_lazy("horizon:management:project_users:index")
    page_title = _("Invite User")


class UpdateUserView(forms.ModalFormView):
    form_class = users_forms.UpdateUserForm
    form_id = "update_user_form"
    modal_header = _("Update User")
    submit_label = _("Update User")
    submit_url = 'horizon:management:project_users:update'
    template_name = 'management/project_users/update.html'
    context_object_name = 'project_users'
    success_url = reverse_lazy("horizon:management:project_users:index")
    page_title = _("Update User")

    @memoized.memoized_method
    def get_object(self):
        try:
            return adjutant.user_get(self.request,
                                     self.kwargs['user_id'])
        except Exception:
            msg = _('Unable to retrieve user.')
            url = reverse('horizon:management:project_users:index')
            exceptions.handle(self.request, msg, redirect=url)

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data(**kwargs)
        context['user'] = self.get_object()
        args = (self.kwargs['user_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        user = self.get_object()
        data = {'id': self.kwargs['user_id'],
                'name': user['username'],
                'roles': user['roles'],
                }
        return data


class UsersView(tables.DataTableView):
    table_class = users_tables.UsersTable
    template_name = 'management/project_users/index.html'
    page_title = _("Project Users")

    def get_data(self):
        try:
            return adjutant.user_list(self.request)
        except Exception:
            exceptions.handle(self.request, _('Failed to list users.'))
            return []
