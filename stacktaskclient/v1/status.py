from stacktaskclient.openstack.common.apiclient import base


class StatusManager(base.BaseManager):

    def get(self):
        url = '/status'
        body = self.client.get(url).json()
        return body
