# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
from __future__ import unicode_literals

import unittest

from mock import patch, MagicMock

from cloudify_awssdk.common.tests.test_base import TestBase, mock_decorator
from cloudify_awssdk.ec2.resources.vpn_connection_route\
    import EC2VPNConnectionRoute

from cloudify_awssdk.ec2.resources import vpn_connection_route
from cloudify_awssdk.common import constants


class TestEC2VPNConnectionRoute(TestBase):

    def setUp(self):
        super(TestEC2VPNConnectionRoute, self).setUp()
        self.vpn_connection_route =\
            EC2VPNConnectionRoute("ctx_node",
                                  resource_id=True,
                                  client=True, logger=None)
        mock1 = patch('cloudify_awssdk.common.decorators.aws_resource',
                      mock_decorator)
        mock1.start()
        reload(vpn_connection_route)

    def test_class_create(self):
        params = \
            {
                'DestinationCidrBlock': 'destination_cidr_block',
                'VpnConnectionId': 'vpn_connection_id_test',
            }
        response = None

        self.vpn_connection_route.client = self.make_client_function(
            'create_vpn_connection_route', return_value=response)
        self.assertEqual(self.vpn_connection_route.create(params), None)

    def test_class_delete(self):
        params = \
            {
                'DestinationCidrBlock': 'destination_cidr_block',
                'VpnConnectionId': 'vpn_connection_id_test',
            }
        response = None

        self.vpn_connection_route.client = self.make_client_function(
            'delete_vpn_connection_route', return_value=response)
        self.assertEqual(self.vpn_connection_route.delete(params), None)

    def test_prepare(self):
        ctx = self.get_mock_ctx("EC2VPNConnectionRoute")
        vpn_connection_route.prepare(ctx, 'config')
        self.assertEqual(
            ctx.instance.runtime_properties['resource_config'],
            'config')

    def test_create(self):
        iface = MagicMock()
        ctx = self.get_mock_ctx("EC2VPNConnectionRoute")

        config = \
            {
                'DestinationCidrBlock': 'destination_cidr_block',
                'VpnConnectionId': 'vpn_connection_id_test',
            }
        response = None
        iface.create = self.mock_return(response)
        vpn_connection_route.create(ctx, iface, config)
        self.assertEqual(
            ctx.instance.runtime_properties[constants.EXTERNAL_RESOURCE_ID],
            'vpn_connection_id_test'
        )

    def test_delete(self):
        iface = MagicMock()
        ctx = self.get_mock_ctx("EC2VPNConnectionRoute")
        vpn_connection_route.delete(ctx, iface, {})
        self.assertTrue(iface.delete.called)


if __name__ == '__main__':
    unittest.main()
