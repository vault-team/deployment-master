# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from keystoneclient.v2_0 import client as keystone_client
from novaclient.v2 import client as nova_client

from common.constant import *


# Openstack Util to hold singleton and lazy initialize
# - keystone
# - nova
class OpenstackUtil():
    def __init__(self):
        pass

    keystone_client = None
    nova_client = None

    @classmethod
    def get_keystone_client(cls):
        if cls.keystone_client is None:
            cls.keystone_client = keystone_client.Client(username=OPENSTACK_USERNAME, password=OPENSTACK_PASSWORD,
                                                         tenant_name=PROJECT_ID, auth_url=AUTH_URL)
        return cls.keystone_client

    @classmethod
    def get_nova_client(cls):
        if cls.nova_client is None:
            cls.nova_client = nova_client.Client(username=OPENSTACK_USERNAME, api_key=OPENSTACK_PASSWORD,
                                                 project_id=PROJECT_ID,
                                                 auth_url=AUTH_URL, connection_pool=True)
        return cls.nova_client
