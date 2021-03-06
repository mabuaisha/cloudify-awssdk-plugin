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

from mock import patch, MagicMock
import unittest
from cloudify.state import current_ctx
from cloudify_awssdk.common.tests.test_base import TestBase, CLIENT_CONFIG
from cloudify_awssdk.common.tests.test_base import DELETE_RESPONSE
from cloudify_awssdk.common.tests.test_base import DEFAULT_RUNTIME_PROPERTIES
from cloudify_awssdk.dynamodb.resources import table

# Constants
TABLE_TH = ['cloudify.nodes.Root',
            'cloudify.nodes.aws.dynamodb.Table']

NODE_PROPERTIES = {
    'resource_id': 'node_resource_id',
    'use_external_resource': False,
    'resource_config': {},
    'client_config': CLIENT_CONFIG
}

RUNTIME_PROPERTIES_AFTER_CREATE = {
    'aws_resource_id': 'aws_table_name',
    'resource_config': {},
    'aws_resource_arn': 'aws_table_arn'
}


class TestDynamoDBTable(TestBase):

    def setUp(self):
        super(TestDynamoDBTable, self).setUp()

        self.fake_boto, self.fake_client = self.fake_boto_client('dynamodb')

        self.mock_patch = patch('boto3.client', self.fake_boto)
        self.mock_patch.start()

    def tearDown(self):
        self.mock_patch.stop()
        self.fake_boto = None
        self.fake_client = None

        super(TestDynamoDBTable, self).tearDown()

    def test_create_raises_UnknownServiceError(self):
        self._prepare_create_raises_UnknownServiceError(
            type_hierarchy=TABLE_TH,
            type_name='dynamodb',
            type_class=table
        )

    def test_create(self):
        _ctx = self.get_mock_ctx(
            'test_create',
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=DEFAULT_RUNTIME_PROPERTIES,
            type_hierarchy=TABLE_TH
        )

        current_ctx.set(_ctx)

        self.fake_client.create_table = MagicMock(return_value={
            'TableDescription': {
                'TableName': 'aws_table_name',
                'TableArn': 'aws_table_arn'
            }
        })

        self.fake_client.describe_table = MagicMock(return_value={
            'Table': {
                'TableStatus': 'ACTIVE'
            }
        })

        table.create(
            ctx=_ctx, resource_config={
                "AttributeDefinitions": [{
                    "AttributeName": "RandomKeyUUID",
                    "AttributeType": "S"
                }],
                "KeySchema": [{
                    "AttributeName": "RandomKeyUUID",
                    "KeyType": "HASH"
                }],
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": "5",
                    "WriteCapacityUnits": "5"
                }
            }, iface=None
        )

        self.fake_boto.assert_called_with('dynamodb', **CLIENT_CONFIG)

        self.fake_client.create_table.assert_called_with(
            AttributeDefinitions=[{
                'AttributeName': 'RandomKeyUUID', 'AttributeType': 'S'
            }],
            KeySchema=[{
                'KeyType': 'HASH',
                'AttributeName': 'RandomKeyUUID'
            }],
            ProvisionedThroughput={
                'ReadCapacityUnits': '5',
                'WriteCapacityUnits': '5'
            },
            TableName='aws_resource'
        )

        self.fake_client.describe_table.assert_called_with(
            TableName='aws_table_name'
        )

        self.assertEqual(
            _ctx.instance.runtime_properties,
            RUNTIME_PROPERTIES_AFTER_CREATE
        )

    def test_delete(self):
        _ctx = self.get_mock_ctx(
            'test_delete',
            test_properties=NODE_PROPERTIES,
            test_runtime_properties=RUNTIME_PROPERTIES_AFTER_CREATE,
            type_hierarchy=TABLE_TH
        )

        current_ctx.set(_ctx)

        self.fake_client.delete_table = MagicMock(
            return_value=DELETE_RESPONSE
        )

        table.delete(ctx=_ctx, resource_config=None, iface=None)

        self.fake_boto.assert_called_with('dynamodb', **CLIENT_CONFIG)

        self.fake_client.delete_table.assert_called_with(
            TableName='aws_table_name'
        )

        self.assertEqual(
            _ctx.instance.runtime_properties,
            {
                '__deleted': True,
            }
        )


if __name__ == '__main__':
    unittest.main()
