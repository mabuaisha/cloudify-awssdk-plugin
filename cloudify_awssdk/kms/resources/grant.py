# #######
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
"""
    KMS.KeyGrant
    ~~~~~~~~
    AWS KMS Key Grant interface
"""
# Cloudify
from cloudify_awssdk.common import decorators, utils
from cloudify_awssdk.kms import KMSBase
from cloudify_awssdk.common.constants import EXTERNAL_RESOURCE_ID
# Boto

RESOURCE_TYPE = 'KMS Key Grant'
RESOURCE_NAME = 'Name'
KEY_TYPE = 'cloudify.nodes.aws.kms.CustomerMasterKey'
KEY_ID = 'KeyId'
GRANT_ID = 'GrantId'
GRANT_TOKEN = 'GrantToken'


class KMSKeyGrant(KMSBase):
    """
        AWS KMS Key Grant interface
    """
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        KMSBase.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        return None

    @property
    def status(self):
        """Gets the status of an external resource"""
        return None

    def create(self, params):
        """
            Create a new AWS KMS Key Grant.
        """
        return self.make_client_call('create_grant', params)

    def delete(self, params=None):
        """
            Deletes an existing AWS KMS Key Grant.
        """
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        self.client.revoke_grant(**params)


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    """Prepares an AWS KMS Key"""
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(KMSKeyGrant, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    """Creates an AWS KMS Key Grant"""
    # Create a copy of the resource config for clean manipulation.
    params = \
        dict() if not resource_config else resource_config.copy()
    resource_id = \
        utils.get_resource_id(
            ctx.node,
            ctx.instance,
            params.get(RESOURCE_NAME),
            use_instance_id=True
        )
    params[RESOURCE_NAME] = resource_id
    utils.update_resource_id(ctx.instance, resource_id)

    key_id = params.get(KEY_ID)
    if not key_id:
        target_key = \
            utils.find_rel_by_node_type(
                ctx.instance,
                KEY_TYPE)
        key_id = \
            target_key.target.instance.runtime_properties[EXTERNAL_RESOURCE_ID]
        params[KEY_ID] = key_id
        ctx.instance.runtime_properties[KEY_ID] = key_id

    # Actually create the resource
    output = iface.create(params)
    ctx.instance.runtime_properties[GRANT_TOKEN] = \
        output.get(GRANT_TOKEN)
    utils.update_resource_id(
        ctx.instance,
        output.get(GRANT_ID)
    )


@decorators.aws_resource(KMSKeyGrant,
                         RESOURCE_TYPE,
                         ignore_properties=True)
def delete(ctx, iface, resource_config, **_):
    """Deletes an KMS Key Grant"""

    # Create a copy of the resource config for clean manipulation.
    params = \
        dict() if not resource_config else resource_config.copy()

    key_id = params.get(KEY_ID)
    if not key_id:
        params[KEY_ID] = \
            ctx.instance.runtime_properties[KEY_ID]
    grant_id = params.get(GRANT_ID)
    if not grant_id:
        params[GRANT_ID] = \
            iface.resource_id

    # Actually delete the resource
    iface.delete(params)
