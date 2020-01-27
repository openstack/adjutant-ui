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

from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages

from adjutant_ui import api


class EmailForm(forms.SelfHandlingForm):
    new_email = forms.EmailField(
        label=_("New email address"),
        required=True)

    confirm_email = forms.CharField(
        label=_("Confirm email address"),
        required=True)
    no_autocomplete = True

    def clean(self):
        '''Check to make sure email fields match.'''
        data = super(forms.Form, self).clean()
        if data.get('new_email') != data.get('confirm_email', None):
            raise ValidationError(_('Email addresses do not match.'))
        return data

    def handle(self, request, data):
        try:
            response = api.adjutant.email_update(request, data['new_email'])
            if response.status_code == 202:
                msg = _("Confirmation email sent to %s.")
                messages.success(request, msg % data['new_email'])
            elif response.status_code == 400:
                messages.warning(request, _(
                    'Unable to update email. May already be in use.'))
            else:
                messages.error(request, _('Failed to update email.'))
            return True
        except Exception as e:
            messages.error(request, _('Failed to update email. %s' % str(e)))
            return False
