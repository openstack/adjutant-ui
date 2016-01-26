#tokens class

from stacktaskclient.common import utils

import six
from six.moves.urllib import parse

from stacktaskclient.openstack.common.apiclient import base


class Token(base.Resource):
    pass


class TokenParam(base.Resource):
    pass


class TokenManager(base.BaseManager):
    resource_class = Token

    def show(self, token_id):
        """Get details on a particular token object"""
        url = 'tokens/%s' % token_id
        return [self._get(url)]

    def submit(self, token_id, parameters):
        url = 'tokens/%s' % token_id
        json = parameters
        return self._post(url, json)

    def reissue(self, task_id):
        """ Given a task id, reissues the tokens associated with that task """
        url = 'tokens'
        json = {
            'task': task_id
        }
        return self._post(url, json)
