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

import logging
import six
import json

from osc_lib.command import command
from osc_lib.i18n import _


LOG = logging.getLogger(__name__)


def _show_task(task_id, client, formatter):
    task = client.tasks.get(task_id)
    if formatter == 'table':
        task._info['actions'] = json.dumps(
            getattr(task, 'actions', ""), indent=2)
        task._info['keystone_user'] = json.dumps(
            getattr(task, 'keystone_user', ""), indent=2)
        task._info['action_notes'] = json.dumps(
            getattr(task, 'action_notes', ""), indent=2)
        task._info['approved_by'] = json.dumps(
            getattr(task, 'approved_by', ""), indent=2)
    return zip(*six.iteritems(task.to_dict()))


class TaskList(command.Lister):
    """Lists adjutant tasks. """

    def get_parser(self, prog_name):
        parser = super(TaskList, self).get_parser(prog_name)

        parser.add_argument(
            '--limit', metavar='<limit>',
            required=False,
            help=_('Limit the number of task responses.'))
        parser.add_argument(
            '--filters', metavar='<filters>',
            required=False,
            help=_('JSON containing filters for the tasks.'),
            default={})

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration

        kwargs = {'filters': parsed_args.filters}

        if parsed_args.limit:
            kwargs['tasks_per_page'] = parsed_args.limit

        tasks = client.tasks.list(**kwargs)

        headers = [
            'UUID', 'Task Type', 'Created on',
            'Approved on', 'Completed on', 'Cancelled']

        rows = [[task.uuid, task.task_type, task.created_on,
                 task.approved_on, task.completed_on, task.cancelled]
                for task in tasks]

        return headers, rows


class TaskShow(command.ShowOne):
    """Show details of one task."""

    def get_parser(self, prog_name):
        parser = super(TaskShow, self).get_parser(prog_name)

        parser.add_argument(
            'task_id', metavar='<taskid>',
            help=_("The task ID."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        return _show_task(parsed_args.task_id, client, parsed_args.formatter)


class TaskApprove(command.ShowOne):
    """ Approve and show details of a task."""
    def get_parser(self, prog_name):
        parser = super(TaskApprove, self).get_parser(prog_name)

        parser.add_argument(
            'task_id', metavar='<taskid>',
            help=_("The task ID."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        client.tasks.approve(parsed_args.task_id)
        return _show_task(parsed_args.task_id, client, parsed_args.formatter)


class TaskCancel(command.ShowOne):
    """ Approve and show details of a task."""
    def get_parser(self, prog_name):
        parser = super(TaskCancel, self).get_parser(prog_name)

        parser.add_argument(
            'task_id', metavar='<taskid>',
            help=_("The task ID."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        client.tasks.cancel(task_id=parsed_args.task_id)
        return _show_task(parsed_args.task_id, client, parsed_args.formatter)


class TaskUpdate(command.ShowOne):
    """Update data and re-run pre-approve for a task."""
    def get_parser(self, prog_name):
        parser = super(TaskUpdate, self).get_parser(prog_name)

        parser.add_argument(
            'task_id', metavar='<taskid>',
            help=_("The task ID."))
        parser.add_argument(
            'data', metavar='<data>',
            help=_("New JSON action data."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        client.tasks.update(task_id=parsed_args.task_id,
                            data=json.loads(parsed_args.data))
        return _show_task(parsed_args.task_id, client, parsed_args.formatter)


class TaskTokenReissue(command.Command):
    """ Reissues a token for the provided pending task """
    def get_parser(self, prog_name):
        parser = super(TaskTokenReissue, self).get_parser(prog_name)

        parser.add_argument('task_id', metavar='<task_id>',
                            help=_('The task ID.'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.registration
        resp = client.tokens.reissue(task_id=parsed_args.task_id)
        print('Success', ' '.join(resp.notes))
