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

from django.shortcuts import render
from django.urls import reverse_lazy

from horizon import forms

from adjutant_ui.content.signup import forms as su_forms


class SignupFormView(forms.ModalFormView):
    form_class = su_forms.SignupForm
    submit_url = reverse_lazy("horizon:signup:signup:index")
    success_url = reverse_lazy("horizon:signup:signup:submitted")
    template_name = 'signup/index.html'


def signup_sent_view(request):
    return render(request, 'signup/submitted.html')
