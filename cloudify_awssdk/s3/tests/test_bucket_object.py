# Copyright (c) 2018 GigaSpaces Technologies Ltd. All rights reserved
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

# Standard Imports
import unittest
import datetime
import tempfile
from dateutil.tz import tzutc

# Third Party Imports
from mock import patch, MagicMock

# Local Imports
from cloudify_awssdk.common.tests.test_base import TestBase, mock_decorator
from cloudify_awssdk.s3.resources.bucket_object import (S3BucketObject, BUCKET)
from cloudify_awssdk.common.constants import EXTERNAL_RESOURCE_ID
from cloudify_awssdk.s3.resources import bucket_object

PATCH_PREFIX = 'cloudify_awssdk.s3.resources.bucket_object.'

RESOURCE_CONFIG = {
    'resource_config': {
        'kwargs': {

        }
    }
}


class TestS3BucketObject(TestBase):

    def setUp(self):
        super(TestS3BucketObject, self).setUp()
        self.resource_config = RESOURCE_CONFIG
        self.resource_config['resource_config']['kwargs'] = \
            {BUCKET: 'test_bucket'}
        self.ctx = self.get_mock_ctx(test_name="Backet",
                                     test_properties=self.resource_config)

        self.bucket_object = S3BucketObject(self.ctx.node,
                                            resource_id=True,
                                            client=True,
                                            logger=None)
        mock1 = patch('cloudify_awssdk.common.decorators.aws_resource',
                      mock_decorator)
        mock1.start()
        reload(bucket_object)

    def test_class_properties(self):
        effect = self.get_client_error_exception(name='S3 Bucket Object')

        self.bucket_object.client =\
            self.make_client_function('head_object', side_effect=effect)

        res = self.bucket_object.properties
        self.assertIsNone(res)

        value = \
            {
                u'AcceptRanges': 'bytes',
                u'ContentType': 'binary/octet-stream',
                'ResponseMetadata': {
                    'HTTPStatusCode': 200,
                    'RetryAttempts': 0,
                    'HostId': 'yI9qpNslqa6e52uec3pXkxr'
                              'K3m309lWdTEBwzIHfkM3Z/a'
                              'X5vhFDU6l+cl2yf8w1WYclKPbqZJA=',
                    'RequestId': '941675782C2A4AA8',
                    'HTTPHeaders': {
                        'content-length': '40',
                        'x-amz-id-2': 'yI9qpNslqa6e52uec3pXkxr'
                                      'K3m309lWdTEBwzIHfkM3Z/aX'
                                      '5vhFDU6l+cl2yf8w1WYclKPbqZJA=',
                        'accept-ranges': 'bytes',
                        'server': 'AmazonS3',
                        'last-modified': 'Tue, 10 Jul 2018 11:17:40 GMT',
                        'x-amz-request-id': '941675782C2A4AA8',
                        'etag': '"1e3f27797e784c874944e6feb115df7a"',
                        'date': 'Tue, 10 Jul 2018 11:17:49 GMT',
                        'content-type': 'binary/octet-stream'
                    }
                },
                u'LastModified': datetime.datetime(2018, 7, 10, 11, 17, 40,
                                                   tzinfo=tzutc()),
                u'ContentLength': 40,
                u'ETag': '"1e3f27797e784c874944e6feb115df7a"',
                u'Metadata': {}
            }
        self.bucket_object.client =\
            self.make_client_function('head_object', return_value=value)
        res = self.bucket_object.properties
        self.assertEqual(res, value)

        self.bucket_object.client =\
            self.make_client_function('head_object', return_value={})
        res = self.bucket_object.properties
        self.assertEqual(res, {})

    def test_class_status(self):
        self.bucket_object.client =\
            self.make_client_function('head_object', return_value={})

        res = self.bucket_object.status
        self.assertIsNone(res)

        value = \
            {
                u'AcceptRanges': 'bytes',
                u'ContentType': 'binary/octet-stream',
                'ResponseMetadata': {
                    'HTTPStatusCode': 200,
                    'RetryAttempts': 0,
                    'HostId': 'yI9qpNslqa6e52uec3pXkxr'
                              'K3m309lWdTEBwzIHfkM3Z/a'
                              'X5vhFDU6l+cl2yf8w1WYclKPbqZJA=',
                    'RequestId': '941675782C2A4AA8',
                    'HTTPHeaders': {
                        'content-length': '40',
                        'x-amz-id-2': 'yI9qpNslqa6e52uec3pXkxr'
                                      'K3m309lWdTEBwzIHfkM3Z/aX'
                                      '5vhFDU6l+cl2yf8w1WYclKPbqZJA=',
                        'accept-ranges': 'bytes',
                        'server': 'AmazonS3',
                        'last-modified': 'Tue, 10 Jul 2018 11:17:40 GMT',
                        'x-amz-request-id': '941675782C2A4AA8',
                        'etag': '"1e3f27797e784c874944e6feb115df7a"',
                        'date': 'Tue, 10 Jul 2018 11:17:49 GMT',
                        'content-type': 'binary/octet-stream'
                    }
                },
                u'LastModified': datetime.datetime(2018, 7, 10, 11, 17, 40,
                                                   tzinfo=tzutc()),
                u'ContentLength': 40,
                u'ETag': '"1e3f27797e784c874944e6feb115df7a"',
                u'Metadata': {}
            }
        self.bucket_object.client =\
            self.make_client_function('head_object',
                                      return_value=value)
        res = self.bucket_object.status
        self.assertEqual(res, 'available')

    def test_class_create(self):
        value = None
        self.bucket_object.client =\
            self.make_client_function('put_object',
                                      return_value=value)
        bucket_object_request = {
            'Filename': 'test/path/test-object.txt',
            'Bucket': 'test_bucket',
            'Key': 'test-object.txt'
        }
        res = self.bucket_object.create(bucket_object_request)
        self.assertIsNone(res)

    def test_class_delete(self):
        params = {
            'Bucket': 'test_bucket',
            'Key': 'test-object.txt'
        }
        self.bucket_object.client = self.make_client_function('delete_object')
        self.bucket_object.delete(params)
        self.assertTrue(self.bucket_object.client.delete_object.called)

    def test_prepare(self):
        ctx = self.get_mock_ctx("Backet")
        bucket_object.prepare(ctx, 'config')
        self.assertEqual(
            ctx.instance.runtime_properties['resource_config'], 'config')

    def test_create(self):
        bucket_object_request = {
            'Body': 'test/path/test-object.txt',
            'Key': 'test-object.txt'
        }
        config = self.resource_config['resource_config']['kwargs']
        config.update(**bucket_object_request)

        iface = MagicMock()
        iface.create = self.mock_return(None)

        download_file_mock = MagicMock()
        _, file_path = tempfile.mkstemp()
        download_file_mock.return_value = file_path
        bucket_object.download_resource_file = download_file_mock

        bucket_object.create(ctx=self.ctx,
                             iface=iface,
                             resource_config=config)

        self.assertEqual(
            self.ctx.instance.runtime_properties[BUCKET], 'test_bucket')

        self.assertEqual(
            self.ctx.instance.runtime_properties[EXTERNAL_RESOURCE_ID],
            'test-object.txt')

    def test_delete(self):
        iface = MagicMock()
        iface.resource_id = 'test-object.txt'
        self.ctx.instance.runtime_properties[BUCKET] = 'test_bucket'
        bucket_object.delete(ctx=self.ctx, iface=iface, resource_config={})
        self.assertTrue(iface.delete.called)


if __name__ == '__main__':
    unittest.main()
