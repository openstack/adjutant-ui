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

from collections import defaultdict

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from adjutant_ui.api import adjutant


class InviteUser(tables.LinkAction):
    name = "invite"
    verbose_name = _("Invite User")
    url = "horizon:management:project_users:invite"
    classes = ("ajax-modal",)
    icon = "plus"

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Invited User",
            u"Invited Users",
            count
        )


class ResendInvitation(tables.BatchAction):
    name = "resend"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Resend Invitation",
            u"Resend Invitations",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Invitation re-sent",
            u"Invitations re-sent",
            count
        )

    def allowed(self, request, user=None):
        # Only invited users can be re-invited
        return user.cohort == 'Invited'

    def action(self, request, datum_id):
        user = self.table.get_object_by_id(datum_id)
        adjutant.user_invitation_resend(request, user.id)


class UpdateUser(tables.LinkAction):
    name = "update"
    verbose_name = _("Update User")
    url = "horizon:management:project_users:update"
    classes = ("ajax-modal",)
    icon = "pencil"

    def allowed(self, request, user=None):
        # Currently, we only support updating existing users
        return user.cohort == 'Member'


class RevokeUser(tables.DeleteAction):
    help_text = _("This will remove the selected user(s) from the current "
                  "project.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Revoke User",
            u"Revoke Users",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Revoked User",
            u"Revoked Users",
            count
        )

    def delete(self, request, obj_id):
        user = self.table.get_object_by_id(obj_id)

        # NOTE(dale): There is a different endpoint to revoke an invited user
        #             than an Active user.
        result = None
        if user.cohort == 'Invited':
            # Revoke invite for the user
            result = adjutant.user_revoke(request, user.id)
        else:
            # Revoke all roles from the user.
            # That'll get them out of our project; they keep their account.
            result = adjutant.user_roles_remove(
                request, user.id, user.roles)
        if not result or result.status_code not in [200, 202]:
            exception = exceptions.NotAvailable()
            exception._safe_message = False
            raise exception


class UpdateUserRow(tables.Row):
    ajax = True

    def get_data(self, request, user_id):
        user = adjutant.user_get(request, user_id)
        return user

    def load_cells(self, user=None):
        super(UpdateUserRow, self).load_cells(user)
        user = self.datum
        self.classes.append('category-' + user.cohort)


class CohortFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, value, icon):
            return dict(text=text, value=value, icon=icon)

        buttons = []
        buttons.append(make_dict(_('Project Users'),
                                 'Member',
                                 'fa-user-md'))
        buttons.append(make_dict(_('Invited Users'),
                                 'Invited',
                                 'fa-user'))
        return buttons

    def categorize(self, table, users):
        categorized_users = defaultdict(list)
        for u in users:
            categorized_users[u.cohort].append(u)
        return categorized_users


def UserRoleDisplayFilter(role_list):
    roles = [adjutant.get_role_text(r) for r in role_list]
    return ', '.join(roles)


class UsersTable(tables.DataTable):
    uid = tables.Column('id', verbose_name=_('User ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    email = tables.Column('email', verbose_name=_('Email'))
    roles = tables.Column('roles',
                          verbose_name=_('Roles'),
                          filters=[UserRoleDisplayFilter])
    status = tables.Column('status', verbose_name=_('Status'))
    cohort = tables.Column('cohort',
                           verbose_name=_('Member Type'),
                           hidden=True)

    class Meta(object):
        name = 'users'
        row_class = UpdateUserRow
        verbose_name = _('Users')
        columns = ('id', 'name', 'email', 'roles', 'status', 'cohort')
        table_actions = (CohortFilter, InviteUser, RevokeUser)
        row_actions = (UpdateUser, ResendInvitation, RevokeUser)
        multi_select = True
