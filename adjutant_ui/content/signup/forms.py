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

from django.conf import settings
from django import forms
from django import http
from django.utils.translation import ugettext_lazy as _

from horizon import forms as hforms
from horizon.utils import functions as utils

from adjutant_ui.api import adjutant


class SignupForm(hforms.SelfHandlingForm):
    username = forms.CharField(
        max_length=255, label=_("User Name"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    email = forms.EmailField(label=_("Email"))
    project_name = forms.CharField(label=_("Project Name"), max_length=64)
    setup_network = forms.BooleanField(
        label=_("Create Default Network"),
        help_text=_("Create a basic network during account creation so that "
                    "you can deploy VMs immediately."),
        required=False,
        initial=True)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        if (hasattr(settings, 'USERNAME_IS_EMAIL') and
                getattr(settings, 'USERNAME_IS_EMAIL')):
            self.fields.pop('username')
            self.fields['email'].widget = forms.TextInput(
                attrs={"autofocus": "autofocus"})

    def handle(self, request, data):
        submit_response = adjutant.signup_submit(
            request, data)
        if submit_response.ok:
            return True

        # Send the user back to the login page.
        msg = _("The signup service is currently unavailable. "
                "Please try again later.")
        response = http.HttpResponseRedirect(settings.LOGOUT_URL)
        utils.add_logout_reason(self.request, response, msg)
        return response
