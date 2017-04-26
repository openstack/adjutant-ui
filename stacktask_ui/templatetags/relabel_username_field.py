#
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

from django.conf import settings
from django import template
from django.utils.translation import ugettext_lazy

register = template.Library()


@register.simple_tag(takes_context=True)
def relabel_username_field(context):
    """Takes the username field and relabels it to 'email'.

    Note(dalees):
    This function modifies context inside a template renderer,
    which is really bad practice MVC. In this case we prefer
    not to modify the openstack_auth form module, so changing
    form label directly is our best option. Avoid if you can!
    """

    if (hasattr(settings, 'USERNAME_IS_EMAIL') and
            getattr(settings, 'USERNAME_IS_EMAIL')):
        try:
            context['form'].fields['username'].label = ugettext_lazy('Email')
        except Exception:
            pass
    return u""
