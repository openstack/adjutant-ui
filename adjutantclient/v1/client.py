# Copyright (C) 2016 Catalyst IT Ltd
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

from adjutantclient.common import http
from adjutantclient.v1 import notifications
from adjutantclient.v1 import roles
from adjutantclient.v1 import signup
from adjutantclient.v1 import status
from adjutantclient.v1 import tasks
from adjutantclient.v1 import tokens
from adjutantclient.v1 import users


class Client(object):
    """Client for the Adjutant v1 API.

    :param string endpoint: A user-supplied endpoint URL for the adjutant
                            service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Adjutant v1 API."""
        self.http_client = http._construct_http_client(*args, **kwargs)

        self.users = users.UserManager(self.http_client)
        self.user_roles = roles.UserRoleManager(self.http_client)
        self.managed_roles = roles.ManagedRoleManager(self.http_client)
        self.tokens = tokens.TokenManager(self.http_client)
        self.tasks = tasks.TaskManager(self.http_client)
        self.signup = signup.SignupManager(self.http_client)
        self.notifications = notifications.NotificationManager(
            self.http_client)
        self.status = status.StatusManager(self.http_client)
