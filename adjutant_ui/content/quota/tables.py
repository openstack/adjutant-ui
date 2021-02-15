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

import json

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from openstack_dashboard.dashboards.admin.defaults.tables import (
    get_compute_quota_name, get_volume_quota_name, get_network_quota_name
)

from adjutant_ui.api import adjutant


def to_caps(value):
    return value.title()


def display_as_percent(value):
    if value == "-":
        return value
    return '{:.1%}'.format(value)


def get_quota_name(quota):
    if quota.service == "nova":
        return get_compute_quota_name(quota)
    if quota.service == "cinder":
        return get_volume_quota_name(quota)
    if quota.service == "neutron":
        return get_network_quota_name(quota)

    return quota.name.replace("_", " ").title()


class UpdateQuota(tables.LinkAction):
    name = "update"
    verbose_name = _("Update Quota")
    url = "horizon:management:quota:update"
    classes = ("ajax-modal",)
    icon = "edit"


class CancelQuotaTask(tables.DeleteAction):
    help_text = _("This will cancel the selected quota update.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Cancel Quota Update",
            u"Cancel Quota Updates",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Cancelled Quota Update",
            u"Cancelled Quota Updates",
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
            return task.status == "Awaiting Approval"
        return True


class ViewRegion(tables.LinkAction):
    name = "view_region"
    verbose_name = _("View Region")
    url = "horizon:management:quota:region_detail"


class ViewSize(tables.LinkAction):
    name = "view_size"
    verbose_name = _("View Size")
    url = "horizon:management:quota:size_detail"


class UpdateQuotaRow(tables.Row):
    def load_cells(self, resource=None):
        super(UpdateQuotaRow, self).load_cells(resource)
        resource = self.datum
        if resource.important is False:
            self.attrs['hide'] = True
            self.attrs['style'] = 'display: none;'

        self.attrs['size_blob'] = json.dumps(self.datum.size_blob)


class RegionQuotaDetailTable(tables.DataTable):
    service = tables.Column("service", verbose_name=_("Service"),
                            filters=(adjutant.get_service_type, ))
    name = tables.Column(get_quota_name, verbose_name=_("Resource Name"),)
    value = tables.Column("current_quota", verbose_name=_("Resource Quota"), )
    usage = tables.Column("current_usage", verbose_name=_("Current Usage"))
    percent = tables.Column("percent", verbose_name=_("Percentage of Use"),
                            filters=(display_as_percent, ))


class QuotaDetailUsageTable(tables.DataTable):
    service = tables.Column("service", verbose_name=_("Service"),
                            filters=(adjutant.get_service_type, ))
    name = tables.Column(get_quota_name, verbose_name=_("Resource Name"),)
    value = tables.Column("value", verbose_name=_("Quota Value"), )
    current_quota = tables.Column("current_quota",
                                  verbose_name=_("Current Quota "
                                                 "(Current Region)"), )


class RegionOverviewTable(tables.DataTable):
    region = tables.Column("region", verbose_name=_("Region Name"),
                           link=("horizon:management:quota:region_detail"))
    quota_size = tables.Column("quota_size",
                               verbose_name=_("Current Quota Size"),
                               filters=(to_caps, ))
    preapproved_quotas = tables.Column(
        "preapproved_quotas", filters=(to_caps, ),
        verbose_name=_("Preapproved Quota Sizes *"))

    class Meta(object):
        name = "region_overview"
        row_actions = (UpdateQuota, ViewRegion)
        verbose_name = _("Current Quotas")
        hidden_title = False


class QuotaTasksTable(tables.DataTable):
    quota_size = tables.Column(
        "size",
        verbose_name=_("Proposed Size"),
        filters=(to_caps, ))
    regions = tables.Column("regions", verbose_name=_("For Regions"))
    user = tables.Column("user", verbose_name=_("Requested By"))
    created = tables.Column("created", verbose_name=_("Requested On"))
    valid = tables.Column("valid", verbose_name=_("Valid"))
    stats = tables.Column("status", verbose_name=_("Status"))

    class Meta(object):
        name = "quota_tasks"
        row_actions = (CancelQuotaTask, )
        verbose_name = _("Previous Quota Changes")
        hidden_title = False


class SizeOverviewTable(tables.DataTable):
    id = tables.Column("id", hidden=True)
    size = tables.Column("name", verbose_name=_("Size Name"),
                         filters=(to_caps, ))

    class Meta(object):
        name = "size_overview"
        row_actions = (ViewSize, )
        verbose_name = _("Quota Sizes")
        hidden_title = False


class ChangeSizeDisplayTable(tables.DataTable):
    service = tables.Column("service", verbose_name=_("Service"),
                            filters=(adjutant.get_service_type, ),
                            hidden=True)
    name = tables.Column(get_quota_name, verbose_name=_("Resource"),)
    current_quota = tables.Column("current_quota",
                                  verbose_name=_("Current Quota"), )
    usage = tables.Column("current_usage", verbose_name=_("Current Usage"))
    value = tables.Column("value", verbose_name=_("New Quota Value"), )

    class Meta(object):
        name = 'change_size'
        row_class = UpdateQuotaRow
