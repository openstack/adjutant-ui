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
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from adjutant_ui.api import adjutant


class CancelTask(tables.DeleteAction):
    help_text = _("This will cancel all selected tasks.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Cancel Task",
            u"Cancel Tasks",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Cancelled Task",
            u"Cancelled Tasks",
            count
        )

    def delete(self, request, obj_id):
        result = adjutant.task_cancel(request, obj_id)
        if not result or result.status_code not in [200, 202]:
            exception = exceptions.NotAvailable()
            exception._safe_message = False
            raise exception

    def allowed(self, request, task=None):
        if task:
            return not(
                task.status == "Completed" or task.status == "Cancelled")
        return True


class ApproveTask(tables.BatchAction):
    name = "approve"
    help_text = _("This will approve all of the selected tasks.")
    action_type = "danger"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Approve Task",
            u"Approve Tasks",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Approved Task",
            u"Approved Tasks",
            count
        )

    def action(self, request, obj_id):
        result = adjutant.task_approve(request, obj_id)
        if not result or result.status_code not in [200, 202]:
            exception = exceptions.NotAvailable()
            exception._safe_message = False
            raise exception

    def allowed(self, request, task=None):
        if task:
            return task.valid and not(
                task.status == "Completed" or task.status == "Cancelled")
        return True


class ReissueToken(tables.BatchAction):
    name = "reissue"
    help_text = _("This will reissue tokens for the selected tasks.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Reissue Token",
            u"Reissue Tokens",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Reissued Token",
            u"Reissued Tokens",
            count
        )

    def action(self, request, obj_id):
        result = adjutant.token_reissue(request, obj_id)
        if not result or result.status_code not in [200, 202]:
            exception = exceptions.NotAvailable()
            exception._safe_message = False
            raise exception

    def allowed(self, request, task=None):
        if task:
            return task.status == "Approved; Incomplete"
        return True


class RevalidateTask(tables.BatchAction):
    name = "revalidate"
    help_text = _("Rerun initial validation for the task.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Rerun Validation",
            u"Rerun Validation",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Validation run",
            u"Validation run",
            count
        )

    def action(self, request, obj_id):
        result = adjutant.task_revalidate(request, obj_id)
        if not result or result.status_code not in [200, 202]:
            exception = exceptions.NotAvailable()
            exception._safe_message = False
            raise exception

    def allowed(self, request, task=None):
        if task:
            return task.status == 'Awaiting Approval' and not task.valid
        return True


class ReapproveTask(ApproveTask):
    name = "approve"
    help_text = _("This will approve all of the selected tasks.")
    action_type = "danger"

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Reapprove Task",
            u"Reapprove Tasks",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Reapproved Task",
            u"Reapproved Tasks",
            count
        )


class UpdateTask(tables.LinkAction):
    name = "update"
    verbose_name = _("Update Task")
    url = "horizon:management:tasks:update"
    classes = ("ajax-modal",)

    def allowed(self, request, task=None):
        if task:
            return task.status == 'Awaiting Approval'
        return True


def TaskTypeDisplayFilter(task_type):
    return task_type.replace("_", " ").title()


class TaskTable(tables.DataTable):
    uuid = tables.Column('id', verbose_name=_('Task ID'),
                         hidden=True)
    task_type = tables.Column('task_type', verbose_name=_('Task Type'),
                              filters=[TaskTypeDisplayFilter],
                              link="horizon:management:tasks:detail")
    status = tables.Column('status', verbose_name=_('Status'))
    request_by = tables.Column('request_by', verbose_name=_('Requestee'))
    request_project = tables.Column('request_project',
                                    verbose_name=_('Request Project'))
    valid = tables.Column('valid', verbose_name=_("Actions Valid"))
    created_on = tables.Column('created_on',
                               verbose_name=_('Request Date'))
    page = tables.Column('page', hidden=True)

    class Meta(object):
        name = 'task_table'
        verbose_name = _('Tasks')
        table_actions = (ApproveTask, RevalidateTask, CancelTask)
        row_actions = (ApproveTask, UpdateTask, RevalidateTask, CancelTask, )
        prev_pagination_param = pagination_param = 'task_page'

    def get_prev_marker(self):
        return str(int(self.data[0].page) - 1) if self.data else ''

    def get_marker(self):
        return str(int(self.data[0].page) + 1) if self.data else ''

    def get_object_display(self, obj):
        task_type = obj.task_type.replace("_", " ").title()
        return "%s (%s)" % (task_type, obj.id)


class ApprovedTaskTable(TaskTable):

    class Meta(object):
        name = 'approved_table'
        verbose_name = _('Tasks')
        table_actions = (CancelTask, ReapproveTask, ReissueToken)
        row_actions = (CancelTask, ReapproveTask, ReissueToken)
        prev_pagination_param = pagination_param = 'approved_page'


class CompletedTaskTable(TaskTable):

    class Meta(object):
        name = 'completed_table'
        verbose_name = _('Tasks')
        prev_pagination_param = pagination_param = 'completed_page'


class CancelledTaskTable(TaskTable):

    class Meta(object):
        name = 'cancelled_table'
        verbose_name = _('Tasks')
        prev_pagination_param = pagination_param = 'cancelled_page'
