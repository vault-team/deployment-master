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
import logging
import time

from troveclient.v1 import client
from common.constant import *

POLLING_INTERVAL = 5
MAX_TRY = 100
TRY_WAIT = 5 #second for sleep

def get_trove_client():
    trove = client.Client(OPENSTACK_USERNAME, OPENSTACK_PASSWORD, project_id=PROJECT_ID, auth_url=AUTH_URL)
    return trove


def create_trove_cluster(cluster):

    trove = get_trove_client()
    mppdb_id = cluster.id
    while cluster.task['name'] != 'NONE':
        time.sleep(POLLING_INTERVAL)
        logging.info('Wait for MPPDB %s to become active.' % mppdb_id)
        cluster = trove.clusters.get(mppdb_id)
    mppdb_ip_list = []
    for instance_dict in cluster.instances:
        instance = trove.instances.get(instance_dict['id'])
        mppdb_ip_list.append(instance.ip[0])
    mppdb_ip = mppdb_ip_list[0]

    return mppdb_ip


def delete_trove_cluster(cluster_id):
    """Delete a MPPDB by requesting Trove to delete a cluster by its id."""
    trove = get_trove_client()
    trove.clusters.delete(cluster_id)
