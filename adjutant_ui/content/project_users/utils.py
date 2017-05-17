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

ROLE_TRANSLATIONS = {
    'project_admin': _('Project Admin'),
    'project_mod': _('Project Moderator'),
    '_member_': _('Project Member'),
    'heat_stack_owner': _('Heat Stack Owner'),
    'project_readonly': _('Project Read-only'),
    'compute_start_stop': _('Compute Start/Stop'),
    'object_storage': _('Object Storage')
}


def get_role_text(rname):
    # Gets the role text for a given role.
    # If it doesn't exist will simply return the role name.
    if rname in ROLE_TRANSLATIONS:
        return ROLE_TRANSLATIONS[rname].format()
    return rname
