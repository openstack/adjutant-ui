# Copyright 2013 Centrin Data Systems Ltd.
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

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import forms

from adjutant_ui.content.email \
    import forms as pass_forms


class EmailView(forms.ModalFormView):
    form_class = pass_forms.EmailForm
    form_id = "update_email_modal"
    modal_header = _("Update Email Address")
    modal_id = "update_email_modal"
    page_title = _("Update Email Address")
    submit_label = _("Update")
    submit_url = reverse_lazy("horizon:settings:email:index")
    success_url = reverse_lazy("horizon:settings:email:index")
    template_name = 'settings/email/change.html'
