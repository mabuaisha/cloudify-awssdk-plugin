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

import unittest
from cloudify_awssdk.common.tests.test_base import TestBase, mock_decorator
from cloudify_awssdk.ec2.resources.nat_gateway import EC2NatGateway, \
    NATGATEWAYS, NATGATEWAY_ID, SUBNET_ID, ALLOCATION_ID, SUBNET_TYPE, \
    ELASTICIP_TYPE
from mock import patch, MagicMock
from cloudify_awssdk.ec2.resources import nat_gateway


class TestEC2NatGateway(TestBase):

    def setUp(self):
        self.nat_gateway = EC2NatGateway("ctx_node", resource_id=True,
                                         client=True, logger=None)
        mock1 = patch('cloudify_awssdk.common.decorators.aws_resource',
                      mock_decorator)
        mock2 = patch('cloudify_awssdk.common.decorators.wait_for_status',
                      mock_decorator)
        mock3 = patch('cloudify_awssdk.common.decorators.wait_for_delete',
                      mock_decorator)
        mock1.start()
        mock2.start()
        mock3.start()
        reload(nat_gateway)

    def test_class_properties(self):
        effect = self.get_client_error_exception(name='EC2 NAT Gateway')
        self.nat_gateway.client = self.make_client_function('describe_nat'
                                                            '_gateways',
                                                            side_effect=effect)
        res = self.nat_gateway.properties
        self.assertIsNone(res)

        value = {}
        self.nat_gateway.client = self.make_client_function('describe_nat'
                                                            '_gateways',
                                                            return_value=value)
        res = self.nat_gateway.properties
        self.assertEquals(res, {})

        value = {NATGATEWAYS: [{NATGATEWAY_ID: 'test_name'}]}
        self.nat_gateway.client = self.make_client_function('describe_nat'
                                                            '_gateways',
                                                            return_value=value)
        res = self.nat_gateway.properties
        self.assertEqual(res[NATGATEWAY_ID], 'test_name')

    def test_class_status(self):
        value = {}
        self.nat_gateway.client = self.make_client_function('describe_nat'
                                                            '_gateways',
                                                            return_value=value)
        res = self.nat_gateway.status
        self.assertIsNone(res)

        value = {NATGATEWAYS: [{NATGATEWAY_ID: 'test_name',
                                'State': 'available'}]}
        self.nat_gateway.client = self.make_client_function('describe_nat'
                                                            '_gateways',
                                                            return_value=value)
        res = self.nat_gateway.status
        self.assertEqual(res, 'available')

    def test_class_create(self):
        value = {'NatGateway': {'NatGatewayId': 'test'}}
        self.nat_gateway.client = self.make_client_function('create_nat'
                                                            '_gateway',
                                                            return_value=value)
        res = self.nat_gateway.create(value)
        self.assertEqual(res['NatGateway'], value['NatGateway'])

    def test_class_delete(self):
        params = {}
        self.nat_gateway.client = self.make_client_function('delete_nat'
                                                            '_gateway')
        self.nat_gateway.delete(params)
        self.assertTrue(self.nat_gateway.client.delete_nat_gateway.called)

        params = {NATGATEWAYS: 'NATGateway', SUBNET_ID: 'subnet_id',
                  ALLOCATION_ID: 'allocation_id'}
        self.nat_gateway.delete(params)
        self.assertEqual(params[SUBNET_ID], 'subnet_id')
        self.assertEqual(params[ALLOCATION_ID], 'allocation_id')

    def test_prepare(self):
        ctx = self.get_mock_ctx("NATGateway")
        config = {NATGATEWAY_ID: 'nat_gateway', SUBNET_ID: 'subnet_id',
                  ALLOCATION_ID: 'allocation_id'}
        nat_gateway.prepare(ctx, config)
        self.assertEqual(ctx.instance.runtime_properties['resource_config'],
                         config)

    def test_create(self):
        ctx = self.get_mock_ctx("NATGateway")
        config = {NATGATEWAY_ID: 'nat_gateway', SUBNET_ID: 'subnet_id',
                  ALLOCATION_ID: 'allocation_id'}
        self.nat_gateway.resource_id = config[NATGATEWAY_ID]
        iface = MagicMock()
        iface.create = self.mock_return({'NatGateway': config})
        nat_gateway.create(ctx, iface, config)
        self.assertEqual(self.nat_gateway.resource_id,
                         'nat_gateway')

    def test_create_with_relationships(self):
        ctx = self.get_mock_ctx("NatGateway", type_hierarchy=[SUBNET_TYPE,
                                                              ELASTICIP_TYPE])
        config = {NATGATEWAY_ID: 'nat_gateway'}
        self.nat_gateway.resource_id = config[NATGATEWAY_ID]
        iface = MagicMock()
        iface.create = self.mock_return({'NatGateway': config})
        with patch('cloudify_awssdk.common.utils.find_rel_by_node_type'):
            nat_gateway.create(ctx, iface, config)
            self.assertEqual(self.nat_gateway.resource_id,
                             'nat_gateway')

    def test_delete(self):
        iface = MagicMock()
        nat_gateway.delete(iface, {})
        self.assertTrue(iface.delete.called)


if __name__ == '__main__':
    unittest.main()
