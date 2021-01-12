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

import collections
import json
import logging
import requests
from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon.utils import functions as utils
from horizon.utils import memoized

from openstack_dashboard.api import base

LOG = logging.getLogger(__name__)
USER = collections.namedtuple('User',
                              ['id', 'name', 'email',
                               'roles', 'cohort', 'status'])
TOKEN = collections.namedtuple('Token',
                               ['action'])

TASK = collections.namedtuple('Task',
                              ['id', 'task_type', 'valid',
                               'request_by', 'request_project',
                               'created_on', 'approved_on', 'page',
                               'completed_on', 'actions', 'status'])

NOTIFICATION = collections.namedtuple('Notification',
                                      ['uuid', 'notes', 'error', 'created_on',
                                       'acknowledged', 'task'])

QUOTA_SIZE = collections.namedtuple('QuotaSize',
                                    ['id', 'name', 'cinder',
                                     'nova', 'neutron'])

REGION_QUOTA = collections.namedtuple('RegionQuota',
                                      ['id', 'region',
                                       'quota_size', 'preapproved_quotas'])

REGION_QUOTA_VALUE = collections.namedtuple('RegionQuotaValue',
                                            ['id', 'name',
                                             'service', 'current_quota',
                                             'current_usage', 'percent',
                                             'size_blob', 'important'])

SIZE_QUOTA_VALUE = collections.namedtuple('SizeQuotaValue',
                                          ['id', 'name', 'service',
                                           'value', 'current_quota',
                                           'current_usage', 'percent'])

QUOTA_TASK = collections.namedtuple(
    'QuotaTask',
    ['id', 'regions', 'size', 'user', 'created', 'valid', 'status'])


# NOTE(amelia): A list of quota names that we consider to be the most
# relevant to customers to be shown initially on the update page.
# These can be overriden in the local_settings file:
# IMPORTANT_QUOTAS = {<service>: [<quota_name>], }
IMPORTANT_QUOTAS = {
    'nova': [
        'instances', 'cores', 'ram',
    ],
    'cinder': [
        'volumes', 'snapshots', 'gigabytes',
    ],
    'neutron': [
        'network', 'floatingip', 'router', 'security_group',
    ],
    'octavia': [
        'load_balancer',
    ],
}


# NOTE(adriant): Quotas that should be hidden by default.
# Can be overriden in the local_settings file by setting:
# HIDDEN_QUOTAS = {<service>: [<quota_name>], }
# or disabled entirely with: HIDDEN_QUOTAS = {}
HIDDEN_QUOTAS = {
    # these values have long since been deprecated from Nova
    'nova': [
        'security_groups', 'security_group_rules',
        'floating_ips', 'fixed_ips',
    ],
    # these by default have no limit
    'cinder': [
        'per_volume_gigabytes', 'volumes_lvmdriver-1',
        'gigabytes_lvmdriver-1', 'snapshots_lvmdriver-1',

    ],
    'neutron': [
        'subnetpool',
    ],
}


ROLE_TRANSLATIONS = {
    'project_admin': _('Project Administrator'),
    'project_mod': _('Project Moderator'),
    '_member_': _('Project Member'),
    'Member': _('Project Member'),
    'heat_stack_owner': _('Heat Stack Owner'),
    'project_readonly': _('Project Read-only'),
    'compute_start_stop': _('Compute Start/Stop'),
    'object_storage': _('Object Storage')
}


def get_role_text(name):
    # Gets the role text for a given role.
    # If it doesn't exist will simply return the role name.
    role_translations = getattr(settings, 'ROLE_TRANSLATIONS', None)
    if role_translations is None:
        role_translations = ROLE_TRANSLATIONS
    if name in role_translations:
        return role_translations[name].format()
    return name


SERVICE_TRANSLATIONS = {
    'cinder': _('Volume'),
    'neutron': _('Networking'),
    'nova': _('Compute'),
    'octavia': _('Load Balancer'),
}


def get_service_type(name):
    # Takes service names and returns a 'nice' name of where they
    # are from
    service_translations = getattr(settings, 'SERVICE_TRANSLATIONS', None)
    if service_translations is None:
        service_translations = SERVICE_TRANSLATIONS
    if name in service_translations:
        return service_translations[name].format()
    return name


class AdjutantApiError(BaseException):
    pass


def _get_endpoint_url(request):
    # If the request is made by an anonymous user, this endpoint request fails.
    # Thus, we must hardcode this in Horizon.
    if getattr(request.user, "service_catalog", None):
        try:
            url = base.url_for(request, service_type='admin-logic')
        except exceptions.ServiceCatalogException:
            url = base.url_for(request, service_type='registration')
    else:
        try:
            url = getattr(settings, 'OPENSTACK_ADJUTANT_URL')
        except AttributeError:
            url = getattr(settings, 'OPENSTACK_REGISTRATION_URL')

    # Ensure ends in slash
    if not url.endswith('/'):
        url += '/'

    return url


def _request(request, method, url, headers, **kwargs):
    try:
        endpoint_url = _get_endpoint_url(request)
        url = urljoin(endpoint_url, url)
        session = requests.Session()
        data = kwargs.pop("data", None)
        return session.request(method, url, headers=headers,
                               data=data, **kwargs)
    except Exception as e:
        LOG.error(e)
        raise


def head(request, url, **kwargs):
    return _request(request, 'HEAD', url, **kwargs)


def get(request, url, **kwargs):
    return _request(request, 'GET', url, **kwargs)


def post(request, url, **kwargs):
    return _request(request, 'POST', url, **kwargs)


def put(request, url, **kwargs):
    return _request(request, 'PUT', url, **kwargs)


def patch(request, url, **kwargs):
    return _request(request, 'PATCH', url, **kwargs)


def delete(request, url, **kwargs):
    return _request(request, 'DELETE', url, **kwargs)


def user_invite(request, user):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    user['project_id'] = request.user.tenant_id
    return post(request, 'openstack/users',
                headers=headers, data=json.dumps(user))


def user_list(request):
    users = []
    try:
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': request.user.token.id}
        resp = json.loads(get(request, 'openstack/users',
                              headers=headers).content)

        for user in resp['users']:
            users.append(
                USER(
                    id=user['id'],
                    name=user['name'],
                    email=user['email'],
                    roles=user['roles'],
                    status=user['status'],
                    cohort=user['cohort']
                )
            )
    except Exception as e:
        LOG.error(e)
        raise
    return users


def user_get(request, user_id):
    try:
        headers = {'X-Auth-Token': request.user.token.id}
        resp = get(request, 'openstack/users/%s' % user_id,
                   headers=headers).content
        return json.loads(resp)
    except Exception as e:
        LOG.error(e)
        raise


def user_roles_update(request, user):
    try:
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': request.user.token.id}
        user['project_id'] = request.user.tenant_id
        user['roles'] = user.roles
        return put(request, 'openstack/users/%s/roles' % user['id'],
                   headers=headers,
                   data=json.dumps(user))
    except Exception as e:
        LOG.error(e)
        raise


def user_roles_add(request, user_id, roles):
    try:
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': request.user.token.id}
        params = {}
        params['project_id'] = request.user.tenant_id
        params['roles'] = roles
        return put(request, 'openstack/users/%s/roles' % user_id,
                   headers=headers,
                   data=json.dumps(params))
    except Exception as e:
        LOG.error(e)
        raise


def user_roles_remove(request, user_id, roles):
    try:
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': request.user.token.id}
        params = {}
        params['project_id'] = request.user.tenant_id
        params['roles'] = roles
        return delete(request, 'openstack/users/%s/roles' % user_id,
                      headers=headers,
                      data=json.dumps(params))
    except Exception as e:
        LOG.error(e)
        raise


def user_revoke(request, user_id):
    try:
        headers = {'Content-Type': 'application/json',
                   'X-Auth-Token': request.user.token.id}
        data = dict()
        return delete(request, 'openstack/users/%s' % user_id,
                      headers=headers,
                      data=json.dumps(data))
    except Exception as e:
        LOG.error(e)
        raise


def user_invitation_resend(request, user_id):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    # For non-active users, the task id is the same as their userid
    # For active users, re-sending an invitation doesn't make sense.
    data = {
        "task": user_id
    }
    return post(request, 'tokens',
                headers=headers,
                data=json.dumps(data))


def valid_roles_get(request):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    role_data = get(request, 'openstack/roles', headers=headers)
    return role_data.json()


def valid_role_names_get(request):
    roles_data = valid_roles_get(request)
    role_names = [r['name'] for r in roles_data['roles']]
    return role_names


def token_get(request, token, data):
    headers = {'Content-Type': 'application/json'}
    return get(request, 'tokens/%s' % token,
               data=json.dumps(data), headers=headers)


def token_submit(request, token, data):
    headers = {"Content-Type": "application/json"}
    return post(request, 'tokens/%s' % token,
                data=json.dumps(data), headers=headers)


def token_reissue(request, task_id):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    data = {'task': task_id}
    return post(request, 'tokens/',
                data=json.dumps(data), headers=headers)


def email_update(request, email):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    data = {
        'new_email': email
    }
    return post(request, 'openstack/users/email-update',
                data=json.dumps(data), headers=headers)


def forgotpassword_submit(request, data):
    headers = {"Content-Type": "application/json"}
    try:
        return post(request, 'openstack/users/password-reset',
                    data=json.dumps(data),
                    headers=headers)
    except Exception as e:
        LOG.error(e)
        raise


def signup_submit(request, data):
    headers = {"Content-Type": "application/json"}
    try:
        return post(request, 'openstack/sign-up',
                    data=json.dumps(data),
                    headers=headers)
    except Exception as e:
        LOG.error(e)
        raise


def notification_list(request, filters={}, page=1):
    notifs_per_page = utils.get_page_size(request)
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}

    response = get(request, 'notifications', headers=headers,
                   params={'filters': json.dumps(filters), 'page': page,
                           'notifications_per_page': notifs_per_page})
    if not response.status_code == 200:
        if response.json() == {'error': 'Empty page'}:
            raise AdjutantApiError("Empty Page")
        raise BaseException

    notificationlist = []
    for notification in response.json()['notifications']:
        notificationlist.append(notification_obj_get(
            request, notification=notification))
    has_more = response.json()['has_more']
    has_prev = response.json()['has_prev']
    return notificationlist, has_prev, has_more


def notification_get(request, uuid):
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}

    response = get(request, 'notifications/%s/' % uuid, headers=headers)
    return response


def notification_obj_get(request, notification_id=None, notification=None):
    if not notification:
        notification = notification_get(request, notification_id).json()

    if notification['error']:
        notes = notification['notes'].get('errors')
    else:
        notes = notification['notes'].get('notes')

    if not notes:
        notes = notification['notes']
    if isinstance(notes, list) and len(notes) == 1:
        notes = notes[0]

    if not isinstance(notes, str):
        notes = json.dumps(notes)

    return NOTIFICATION(uuid=notification['uuid'],
                        task=notification['task'],
                        error=notification['error'],
                        created_on=notification['created_on'],
                        acknowledged=notification['acknowledged'],
                        notes=notes)


def notifications_acknowlege(request, notification_id=None):
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}
    # Takes either a single notification id or a list of them
    # and acknowleges all of them
    if isinstance(notification_id, list):
        data = {'notifications': notification_id}
        return post(request, 'notifications', data=json.dumps(data),
                    headers=headers)
    else:
        url = "notifications/%s/" % notification_id
        return post(request, url, data=json.dumps({'acknowledged': True}),
                    headers=headers)


def task_list(request, filters={}, page=1):
    tasks_per_page = utils.get_page_size(request)
    tasklist = []
    prev = more = False
    try:
        headers = {"Content-Type": "application/json",
                   'X-Auth-Token': request.user.token.id}
        params = {
            "filters": json.dumps(filters),
            "page": page,
            "tasks_per_page": tasks_per_page
        }
        resp = get(request, "tasks", params=params, data=json.dumps({}),
                   headers=headers).json()
        prev = resp['has_prev']
        more = resp['has_more']
        for task in resp['tasks']:
            tasklist.append(task_obj_get(request, task=task, page=page))
        return tasklist, prev, more
    except Exception as e:
        LOG.error(e)
        raise


def task_get(request, task_id):
    # Get a single task
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}

    return get(request, "tasks/%s" % task_id,
               headers=headers)


def task_obj_get(request, task_id=None, task=None, page=0):
    if not task:
        task = task_get(request, task_id).json()

    status = "Awaiting Approval"
    if task['cancelled']:
        status = "Cancelled"
    elif task['completed_on']:
        status = "Completed"
    elif task['approved_on']:
        status = "Approved; Incomplete"

    valid = False not in [action['valid'] for
                          action in task['actions']]
    return TASK(
        id=task['uuid'],
        task_type=task['task_type'],
        valid=valid,
        request_by=task['keystone_user'].get('username', '-'),
        request_project=task['keystone_user'].get('project_name', '-'),
        status=status,
        created_on=task['created_on'],
        approved_on=task['approved_on'],
        completed_on=task['completed_on'],
        actions=task['actions'],
        page=page
    )


def task_cancel(request, task_id):
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}

    return delete(request, "tasks/%s" % task_id,
                  headers=headers)


def task_approve(request, task_id):
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}

    return post(request, "tasks/%s" % task_id,
                data=json.dumps({"approved": True}), headers=headers)


def task_update(request, task_id, new_data):
    headers = {"Content-Type": "application/json",
               'X-Auth-Token': request.user.token.id}

    return put(request, "tasks/%s" % task_id,
               data=new_data, headers=headers)


def task_revalidate(request, task_id):
    task = task_get(request, task_id=task_id).json()

    data = {}
    for action_data in [action['data'] for action in task['actions']]:
        data.update(action_data)

    return task_update(request, task_id, json.dumps(data))


# Quota management functions
def _is_quota_hidden(service, resource):
    hidden_quotas = getattr(settings, 'HIDDEN_QUOTAS', None)
    if hidden_quotas is None:
        hidden_quotas = HIDDEN_QUOTAS
    return service in hidden_quotas and resource in hidden_quotas[service]


def _is_quota_important(service, resource):
    important_quotas = getattr(settings, 'IMPORTANT_QUOTAS', None)
    if important_quotas is None:
        important_quotas = IMPORTANT_QUOTAS
    return (
        service in important_quotas and resource in important_quotas[service])


@memoized.memoized_method
def _get_quota_information(request, regions=None, include_usage=True):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    params = {'include_usage': include_usage}
    if regions:
        params['regions'] = regions
    try:
        return get(request, 'openstack/quotas/',
                   params=params, headers=headers).json()
    except Exception as e:
        LOG.error(e)
        raise


def quota_sizes_get(request, region=None):
    # Gets the list of quota sizes, and a json blob defining what they
    # have for each of the services
    # Region param is useless here, but nedded for memoized decorator to work
    quota_sizes_dict = {}

    resp = _get_quota_information(request, regions=region, include_usage=False)

    for size_name, size in resp['quota_sizes'].items():
        quota_sizes_dict[size_name] = QUOTA_SIZE(
            id=size_name,
            name=size_name,
            cinder=json.dumps(size['cinder'], indent=1),
            nova=json.dumps(size['nova'], indent=1),
            neutron=json.dumps(size['neutron'], indent=1),
        )

    quota_sizes = []
    for size in resp['quota_size_order']:
        quota_sizes.append(quota_sizes_dict[size])

    return quota_sizes


def size_details_get(request, size, region=None):
    """Gets the current details of the size as well as the current region's
    quota
    """
    quota_details = []

    if not region:
        region = request.user.services_region
    resp = _get_quota_information(request, regions=region)

    data = resp['quota_sizes'][size]
    region_data = resp['regions'][0]['current_quota']
    for service, values in data.items():
        if service not in resp['regions'][0]['current_usage']:
            continue
        for resource, value in values.items():
            if _is_quota_hidden(service, resource):
                continue

            usage = resp['regions'][0]['current_usage'][service].get(
                resource)
            try:
                percent = float(usage) / value
            except (TypeError, ZeroDivisionError):
                percent = '-'

            quota_details.append(
                SIZE_QUOTA_VALUE(
                    id=resource,
                    name=resource,
                    service=service,
                    value=value,
                    current_quota=region_data[service][resource],
                    current_usage=usage,
                    percent=percent
                )
            )
    return quota_details


def quota_details_get(request, region):
    quota_details = []

    resp = _get_quota_information(request, regions=region)

    data = resp['regions'][0]['current_quota']

    for service, values in data.items():
        for name, value in values.items():
            if _is_quota_hidden(service, name):
                continue

            try:
                if value < 0:
                    value = 'No Limit'
            except (TypeError):
                pass
            usage = resp['regions'][0]['current_usage'][service].get(name)
            try:
                percent = float(usage) / value
            except (TypeError, ZeroDivisionError):
                percent = '-'

            size_blob = {}
            for size_name, size_data in resp['quota_sizes'].items():
                size_blob[size_name] = size_data[service].get(name, '-')

            if name != 'id':
                quota_details.append(
                    REGION_QUOTA_VALUE(
                        id=name,
                        name=name,
                        service=service,
                        current_quota=value,
                        current_usage=usage,
                        percent=percent,
                        size_blob=size_blob,
                        important=_is_quota_important(service, name)
                    )
                )
    return quota_details


def region_quotas_get(request, region=None):
    quota_details = []

    resp = _get_quota_information(request, regions=region, include_usage=False)

    data = resp['regions']
    for region_values in data:
        quota_details.append(
            REGION_QUOTA(
                id=region_values['region'],
                region=region_values['region'],
                quota_size=region_values['current_quota_size'],
                preapproved_quotas=', '.join(region_values[
                    'quota_change_options'])
            )
        )
    return quota_details


def quota_tasks_get(request, region=None):
    # Region param only used to help with memoized decorator
    quota_tasks = []

    resp = _get_quota_information(request, regions=region, include_usage=False)

    for task in resp['active_quota_tasks']:
        quota_tasks.append(
            QUOTA_TASK(
                id=task['id'],
                regions=', '.join(task['regions']),
                size=task['size'],
                user=task['request_user'],
                created=task['task_created'].split("T")[0],
                valid=task['valid'],
                status=task['status'],
            )
        )
    return quota_tasks


def update_quotas(request, size, regions=[]):
    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': request.user.token.id}
    data = {
        'size': size,
    }
    if regions:
        data['regions'] = regions

    return post(request, 'openstack/quotas/',
                data=json.dumps(data),
                headers=headers)
