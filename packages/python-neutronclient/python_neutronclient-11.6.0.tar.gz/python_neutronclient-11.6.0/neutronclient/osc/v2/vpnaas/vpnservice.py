#    Copyright 2017 FUJITSU LIMITED
#    All Rights Reserved.
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
#

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util
from oslo_log import log as logging

from neutronclient._i18n import _
from neutronclient.osc import utils as osc_utils


LOG = logging.getLogger(__name__)

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('router_id', 'Router', column_util.LIST_BOTH),
    ('subnet_id', 'Subnet', column_util.LIST_BOTH),
    ('flavor_id', 'Flavor', column_util.LIST_BOTH),
    ('is_admin_state_up', 'State', column_util.LIST_BOTH),
    ('status', 'Status', column_util.LIST_BOTH),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('external_v4_ip', 'Ext v4 IP', column_util.LIST_LONG_ONLY),
    ('external_v6_ip', 'Ext v6 IP', column_util.LIST_LONG_ONLY),
)

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'router_id': 'Router',
    'subnet_id': 'Subnet',
    'flavor_id': 'Flavor',
    'is_admin_state_up': 'State',
    'status': 'Status',
    'description': 'Description',
    'project_id': 'Project',
    'external_v4_ip': 'Ext v4 IP',
    'external_v6_ip': 'Ext v6 IP',
}


def _get_common_parser(parser):
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_('Description for the VPN service'))
    parser.add_argument(
        '--subnet',
        metavar='<subnet>',
        help=_('Local private subnet (name or ID)'))
    parser.add_argument(
        '--flavor',
        metavar='<flavor>',
        help=_('Flavor for the VPN service (name or ID)'))
    admin_group = parser.add_mutually_exclusive_group()
    admin_group.add_argument(
        '--enable',
        action='store_true',
        help=_("Enable VPN service")
    )
    admin_group.add_argument(
        '--disable',
        action='store_true',
        help=_("Disable VPN service")
    )
    return parser


def _get_common_attrs(client_manager, parsed_args, is_create=True):
    attrs = {}
    if is_create:
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['project_id'] = osc_utils.find_project(
                client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
    if parsed_args.description:
        attrs['description'] = str(parsed_args.description)
    if parsed_args.subnet:
        _subnet_id = client_manager.network.find_subnet(
            parsed_args.subnet).id
        attrs['subnet_id'] = _subnet_id
    if parsed_args.flavor:
        _flavor_id = client_manager.network.find_flavor(
            parsed_args.flavor,
            ignore_missing=False
        ).id
        attrs['flavor_id'] = _flavor_id
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    return attrs


class CreateVPNService(command.ShowOne):
    _description = _("Create an VPN service")

    def get_parser(self, prog_name):
        parser = super(CreateVPNService, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name for the VPN service'))
        parser.add_argument(
            '--router',
            metavar='ROUTER',
            required=True,
            help=_('Router for the VPN service (name or ID)'))
        osc_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager, parsed_args)
        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.router:
            _router_id = client.find_router(parsed_args.router,
                                            ignore_missing=False).id
            attrs['router_id'] = _router_id
        obj = client.create_vpn_service(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteVPNService(command.Command):
    _description = _("Delete VPN service(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteVPNService, self).get_parser(prog_name)
        parser.add_argument(
            'vpnservice',
            metavar='<vpn-service>',
            nargs='+',
            help=_('VPN service to delete (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for vpn in parsed_args.vpnservice:
            try:
                vpn_id = client.find_vpn_service(vpn,
                                                 ignore_missing=False)['id']
                client.delete_vpn_service(vpn_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete VPN service with "
                            "name or ID '%(vpnservice)s': %(e)s"),
                          {'vpnservice': vpn, 'e': e})

        if result > 0:
            total = len(parsed_args.vpnservice)
            msg = (_("%(result)s of %(total)s vpn service failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListVPNService(command.Lister):
    _description = _("List VPN services that belong to a given project")

    def get_parser(self, prog_name):
        parser = super(ListVPNService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.vpn_services()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long)
        return (headers, (utils.get_dict_properties(s, columns) for s in obj))


class SetVPNSercice(command.Command):
    _description = _("Set VPN service properties")

    def get_parser(self, prog_name):
        parser = super(SetVPNSercice, self).get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name for the VPN service'))
        parser.add_argument(
            'vpnservice',
            metavar='<vpn-service>',
            help=_('VPN service to modify (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_common_attrs(self.app.client_manager,
                                  parsed_args, is_create=False)
        if parsed_args.name:
            attrs['name'] = str(parsed_args.name)
        vpn_id = client.find_vpn_service(parsed_args.vpnservice,
                                         ignore_missing=False)['id']
        try:
            client.update_vpn_service(vpn_id, **attrs)
        except Exception as e:
            msg = (_("Failed to set vpn service '%(vpn)s': %(e)s")
                   % {'vpn': parsed_args.vpnservice, 'e': e})
            raise exceptions.CommandError(msg)


class ShowVPNService(command.ShowOne):
    _description = _("Display VPN service details")

    def get_parser(self, prog_name):
        parser = super(ShowVPNService, self).get_parser(prog_name)
        parser.add_argument(
            'vpnservice',
            metavar='<vpn-service>',
            help=_('VPN service to display (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        vpn_id = client.find_vpn_service(parsed_args.vpnservice,
                                         ignore_missing=False)['id']
        obj = client.get_vpn_service(vpn_id)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, _attr_map_dict, ['location', 'tenant_id'])
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)
