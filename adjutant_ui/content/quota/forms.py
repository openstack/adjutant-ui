# Copyright 2016 Catalyst IT Ltd
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

from django.urls import reverse  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from adjutant_ui.api import adjutant


LOG = logging.getLogger(__name__)


class UpdateQuotaForm(forms.SelfHandlingForm):
    region = forms.CharField(label=_("Region"))
    region.widget.attrs['readonly'] = True
    size = forms.ChoiceField(label=_("Size"))
    size.widget.attrs['onchange'] = 'updateSizeTable()'

    failure_url = 'horizon:management:quota:index'
    submit_url = 'horizon:management:quota:update'
    success_url = "horizon:management:quota:index"

    def __init__(self, *args, **kwargs):
        size_choices = kwargs.pop('size_choices')
        super(UpdateQuotaForm, self).__init__(*args, **kwargs)
        self.fields['size'].choices = size_choices

    def handle(self, request, data):
        try:
            response = adjutant.update_quotas(request, data['size'],
                                              regions=[data['region']])
            if response.status_code == 202:
                messages.success(request, _('Task created and may require '
                                            'admin approval.'))
            elif response.status_code == 400:
                messages.error(request, _('Failed to update quota. You may'
                                          ' have usage over the new values '
                                          'that you are attempting to update'
                                          ' the quota to.'))
            else:
                messages.error(request, _('Failed to update quota.'))
            return True
        except Exception:
            msg = _('Failed to update quota.')
            url = reverse('horizon:management:quota:index')
            exceptions.handle(request, msg, redirect=url)
            return False
