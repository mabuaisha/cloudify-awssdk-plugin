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
    EC2.ElasticIP
    ~~~~~~~~~~~~~~
    AWS EC2 ElasticIP interface
"""
# Cloudify
from cloudify_boto3.common import decorators, utils
from cloudify_boto3.ec2 import EC2Base
from cloudify_boto3.common.constants import EXTERNAL_RESOURCE_ID
# Boto
from botocore.exceptions import ClientError

RESOURCE_TYPE = 'EC2 Ellastic IP'
ADDRESSES = 'Addresses'
ELASTICIP_ID = 'PublicIp'
ELASTICIP_IDS = 'PublicIps'
INSTANCE_ID = 'InstanceId'
INSTANCE_TYPE_DEPRECATED = 'cloudify.aws.nodes.Instance'
NETWORKINTERFACE_ID = 'NetworkInterfaceId'
NETWORKINTERFACE_TYPE = 'cloudify.nodes.aws.ec2.Interface'
NETWORKINTERFACE_TYPE_DEPRECATED = 'cloudify.aws.nodes.Interface'
ALLOCATION_ID = 'AllocationId'


class EC2ElasticIP(EC2Base):
    """
        EC2 EC2ElasticIP interface
    """
    def __init__(self, ctx_node, resource_id=None, client=None, logger=None):
        EC2Base.__init__(self, ctx_node, resource_id, client, logger)
        self.type_name = RESOURCE_TYPE

    @property
    def properties(self):
        """Gets the properties of an external resource"""
        params = {ELASTICIP_IDS: [self.resource_id]}
        try:
            resources = \
                self.client.describe_addresses(**params)
        except ClientError:
            pass
        else:
            return resources.get(ADDRESSES)[0] if resources else None

    def create(self, params):
        """
            Create a new AWS EC2 EC2ElasticIP.
        """
        self.logger.debug('Creating %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.allocate_address(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def delete(self, params=None):
        """
            Deletes an existing AWS EC2 ElasticIP.
        """
        self.logger.debug('Deleting %s with parameters: %s'
                          % (self.type_name, params))
        res = self.client.release_address(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def attach(self, params):
        '''
            Attach an AWS EC2 ElasticIP to an Instance or a NetworkInterface.
        '''
        self.logger.debug('Attaching %s with: %s'
                          % (self.type_name, params.get(INSTANCE_ID, None) or
                             params.get(ELASTICIP_ID, None)))
        res = self.client.associate_address(**params)
        self.logger.debug('Response: %s' % res)
        return res

    def detach(self, params):
        '''
            Detach an AWS EC2 ElasticIP from an Instance or a NetworkInterface.
        '''
        self.logger.debug('Detaching %s from: %s'
                          % (self.type_name, params.get(INSTANCE_ID, None) or
                             params.get(ELASTICIP_ID, None)))
        self.logger.debug('Attaching default %s'
                          % (self.type_name))
        res = self.client.disassociate_address(**params)
        self.logger.debug('Response: %s' % res)
        return res


@decorators.aws_resource(resource_type=RESOURCE_TYPE)
def prepare(ctx, resource_config, **_):
    """Prepares an AWS EC2 ElasticIP"""
    # Save the parameters
    ctx.instance.runtime_properties['resource_config'] = resource_config


@decorators.aws_resource(EC2ElasticIP, RESOURCE_TYPE)
def create(ctx, iface, resource_config, **_):
    """Creates an AWS EC2 ElasticIP"""

    # Create a copy of the resource config for clean manipulation.
    params = \
        dict() if not resource_config else resource_config.copy()

    # Actually create the resource
    elasticip = iface.create(params)
    elasticip_id = elasticip.get(ELASTICIP_ID, '')
    iface.update_resource_id(elasticip_id)
    utils.update_resource_id(ctx.instance, elasticip_id)
    ctx.instance.runtime_properties['allocation_id'] = \
        elasticip.get(ALLOCATION_ID, None)


@decorators.aws_resource(EC2ElasticIP, RESOURCE_TYPE,
                         ignore_properties=True)
def delete(ctx, iface, resource_config, **_):
    """Deletes an AWS EC2 ElasticIP"""

    # Create a copy of the resource config for clean manipulation.
    params = \
        dict() if not resource_config else resource_config.copy()
    allocation_id = ctx.instance.runtime_properties.get('allocation_id', None)

    if allocation_id:
        params.update({ALLOCATION_ID: allocation_id})
    else:
        elasticip_id = params.get(ELASTICIP_ID)
        if not elasticip_id:
            elasticip_id = iface.resource_id
        params.update({ELASTICIP_ID: elasticip_id})

    iface.delete(params)


@decorators.aws_resource(EC2ElasticIP, RESOURCE_TYPE)
def attach(ctx, iface, resource_config, **_):
    '''Attaches an AWS EC2 ElasticIP to an Instance or a NetworkInterface'''
    params = dict() if not resource_config else resource_config.copy()

    allocation_id = ctx.instance.runtime_properties.get('allocation_id', None)
    if not allocation_id:
        elasticip_id = params.get(ELASTICIP_ID)
        if not elasticip_id:
            elasticip_id = iface.resource_id
        params.update({ELASTICIP_ID: elasticip_id})
    else:
        params.update({ALLOCATION_ID: allocation_id})

    instance_id = params.get(INSTANCE_ID)
    if not instance_id:
        targ = \
            utils.find_rel_by_node_type(ctx.instance, INSTANCE_TYPE_DEPRECATED)

        if targ:
            params[INSTANCE_ID] = \
                instance_id or \
                targ.target.instance.runtime_properties\
                .get(EXTERNAL_RESOURCE_ID)

        else:
            eni_id = params.get(NETWORKINTERFACE_ID)
            if not eni_id:
                targ = \
                    utils.find_rel_by_node_type(ctx.instance,
                                                NETWORKINTERFACE_TYPE) \
                    or utils\
                    .find_rel_by_node_type(ctx.instance,
                                           NETWORKINTERFACE_TYPE_DEPRECATED)

                if not targ:
                    return

                params[NETWORKINTERFACE_ID] = \
                    eni_id or \
                    targ.target.instance.runtime_properties\
                        .get(EXTERNAL_RESOURCE_ID)

    domain = params.get('Domain')
    if domain:
        params.pop('Domain')

    # Actually attach the resources
    association_id = iface.attach(params)
    ctx.instance.runtime_properties['association_id'] = \
        association_id.get('AssociationId', None)


@decorators.aws_resource(EC2ElasticIP, RESOURCE_TYPE,
                         ignore_properties=True)
def detach(ctx, iface, resource_config, **_):
    '''Detach an AWS EC2 Elasticip from an Instance or NetworkInterface'''
    params = dict() if not resource_config else resource_config.copy()

    association_id = \
        ctx.instance.runtime_properties.get('association_id', None)
    if not association_id:
        elasticip_id = params.get(ELASTICIP_ID)
        if not elasticip_id:
                elasticip_id = iface.resource_id
        params.update({ELASTICIP_ID: elasticip_id})
    else:
        params.update({'AssociationId': association_id})

    iface.detach(params)
