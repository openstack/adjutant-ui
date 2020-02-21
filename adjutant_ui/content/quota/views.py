# Copyright (c) 2016 Catalyst IT Ltd.
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

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables as horizon_tables

from adjutant_ui.api import adjutant
from adjutant_ui.content.quota import forms as quota_forms
from adjutant_ui.content.quota import tables as quota_tables


class IndexView(horizon_tables.MultiTableView):
    page_title = _("Quota Management")
    table_classes = (quota_tables.RegionOverviewTable,
                     quota_tables.SizeOverviewTable,
                     quota_tables.QuotaTasksTable)
    template_name = 'management/quota/index.html'

    def get_region_overview_data(self):
        try:
            return adjutant.region_quotas_get(self.request)
        except Exception:
            exceptions.handle(self.request, _('Failed to list quota sizes.'))
            return []

    def get_size_overview_data(self):
        try:
            return adjutant.quota_sizes_get(self.request)
        except Exception:
            exceptions.handle(self.request, _('Failed to list quota sizes.'))
            return []

    def get_quota_tasks_data(self):
        try:
            return adjutant.quota_tasks_get(self.request)
        except Exception:
            exceptions.handle(self.request, _('Failed to list quota tasks.'))
            return []


class RegionDetailView(horizon_tables.DataTableView):
    table_class = quota_tables.RegionQuotaDetailTable
    template_name = 'management/quota/region_detail.html'
    page_title = _("'{{ region }}' Quota Details")

    def get_data(self):
        try:
            return adjutant.quota_details_get(self.request,
                                              self.kwargs['region'])
        except Exception:
            exceptions.handle(self.request, _('Failed to list quota sizes.'))
            return []

    def get_context_data(self, **kwargs):
        context = super(RegionDetailView, self).get_context_data(**kwargs)
        context['region'] = self.kwargs['region']
        return context


class QuotaSizeView(horizon_tables.DataTableView):
    table_class = quota_tables.QuotaDetailUsageTable
    template_name = 'management/quota/size_detail.html'
    page_title = _("'{{ size }}' Quota Details")

    def get_data(self):
        try:
            return adjutant.size_details_get(self.request,
                                             size=self.kwargs['size'])
        except Exception:
            exceptions.handle(self.request, _('Failed to list quota size.'))
            return []

    def get_context_data(self, **kwargs):
        # request.user.services_region
        context = super(QuotaSizeView, self).get_context_data(**kwargs)
        context['title'] = _("%s - Quota Details") \
            % self.kwargs['size'].title()
        return context


class RegionUpdateView(forms.ModalFormView, horizon_tables.MultiTableView):
    form_class = quota_forms.UpdateQuotaForm
    table_classes = (quota_tables.ChangeSizeDisplayTable, )
    submit_url = 'horizon:management:quota:update'
    context_object_name = 'ticket'
    template_name = 'management/quota/update.html'
    success_url = reverse_lazy("horizon:management:quota:index")
    page_title = _("Update Quota")

    def get_change_size_data(self):
        try:
            return adjutant.quota_details_get(self.request,
                                              region=self.kwargs['region'])
        except Exception:
            exceptions.handle(self.request, _('Failed to list quota sizes.'))
            return []

    def get_object(self):
        return adjutant.region_quotas_get(self.request,
                                          region=self.kwargs['region'])[0]

    def get_context_data(self, **kwargs):
        context = super(RegionUpdateView, self).get_context_data(**kwargs)
        context['region'] = self.get_object()
        args = (self.kwargs['region'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        context['form'] = self.get_form()
        return context

    def get_form_kwargs(self):
        kwargs = super(RegionUpdateView, self).get_form_kwargs()
        sizes = adjutant.quota_sizes_get(
            self.request, region=self.kwargs['region'])
        kwargs['size_choices'] = []

        region = self.get_object()
        for size in sizes:
            if region.quota_size == size.name:
                continue
            if size.name not in region.preapproved_quotas:
                kwargs['size_choices'].append(
                    [size.id, "%s (requires approval)" % size.name.title()])
            else:
                kwargs['size_choices'].append([size.id, size.name.title()])
        return kwargs

    def get_initial(self):
        region = self.get_object()
        data = {'id': region.id,
                'region': region.region,
                'quota_size': region.quota_size,
                'preapproved_quotas': region.preapproved_quotas
                }
        return data

    def post(self, request, *args, **kwargs):
        # NOTE(amelia): The multitableview overides the form view post
        #               this reinstates it.
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
