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

from common.dao import MPPDBDAO
from common.models import MigrationJob, MPPDB
from common.util.trove_cluster_operations import create_trove_cluster, get_trove_client
from common.util.vertica_db_operations import get_dbadmin_password
from deployment_master.action import Action
from service_management_api.utils import OpenstackUtil
from tests.deployment_master.mppdb_creation_dictionary_for_testing import mppdb_creation_dictionary_for_testing
from common.constant import *


class MPPDBCreation(Action):

    def __init__(self, action, dest_tenant_mppdb_group=None, mppdb_quantity_to_create=None):
        self.action = action
        self.action_map = {}
        self.old_mppdbs = []
        self.new_mppdbs = []
        self.dest_tenant_mppdb_group = dest_tenant_mppdb_group
        self.mppdb_quantity_to_create = mppdb_quantity_to_create

    def addAction(self, action_id, actions):
        self.action_map[action_id] = actions

    def run(self, session, test_case=None):
        logging.info('Start to create MPPDBs.')

        if (test_case is None):
            self.old_mppdbs = MPPDBDAO.get_mppdb_list(session, self.dest_tenant_mppdb_group.tenant_mppdb_group_id)

            for i in range(self.mppdb_quantity_to_create):

                """Create a MPPDB by requesting Trove to create a cluster."""
                cluster_instances = []
                for i in range(self.dest_tenant_mppdb_group.node_quantity):
                    cluster_instances.append({'flavorRef': OpenstackUtil.get_nova_client().flavors.find(name=self.dest_tenant_mppdb_group.flavor).__getattribute__('id'),
                                              'volume': {'size': CLUSTER_VOLUME_SIZE},
                                              'availability_zone': CLUSTER_AVAILABILITY_ZONE})
                    i += 1
                trove = get_trove_client()
                cluster = trove.clusters.create(CLUSTER_NAME, CLUSTER_DATASTORE, CLUSTER_DATASTORE_VERSION, instances=cluster_instances)
                mppdb_id = cluster.id
                mppdb_ip = create_trove_cluster(cluster)

                logging.info('MPPDB %s is successfully created.' % mppdb_id)
                mppdb_password = get_dbadmin_password(mppdb_ip)

                if self.action == "tenant_mppdb_data_movement":
                    # add new mppdb to MPPDB
                    mppdb = MPPDB(mppdb_id=mppdb_id, mppdb_ip=mppdb_ip,
                              tenant_mppdb_group_id=self.dest_tenant_mppdb_group.tenant_mppdb_group_id,
                              mppdb_password=mppdb_password)

                # tenant_mppdb_group_id is set to be -1, since all the mppdbs in the same tenant_mppdb_group are ready
                elif self.action == "mppdb_copy":
                    # add new mppdb to MPPDB
                    mppdb = MPPDB(mppdb_id=mppdb_id, mppdb_ip=mppdb_ip,
                                  tenant_mppdb_group_id=-1,
                                  mppdb_password=mppdb_password)

                session.add(mppdb)
                self.new_mppdbs.append(mppdb)
                session.commit()

        # For testing
        else:
            if test_case == 1:
                self.old_mppdbs = mppdb_creation_dictionary_for_testing.find_old_mppdbs_test_case1(
                    dest_tenant_mppdb_group=self.dest_tenant_mppdb_group)
                self.new_mppdbs = mppdb_creation_dictionary_for_testing.find_new_mppdbs_test_case1(
                    dest_tenant_mppdb_group=self.dest_tenant_mppdb_group)
            elif test_case == 2:
                self.old_mppdbs = mppdb_creation_dictionary_for_testing.find_old_mppdbs_test_case2(
                    dest_tenant_mppdb_group=self.dest_tenant_mppdb_group)
                self.new_mppdbs = mppdb_creation_dictionary_for_testing.find_new_mppdbs_test_case2(
                    dest_tenant_mppdb_group=self.dest_tenant_mppdb_group)
        logging.info('New MPPDBs are successfully created.')

        # Identify whether they are Move or Copy and assign mppdb id for these actions
        for key in self.action_map:
            if self.action_map[key][0].action == MigrationJob._mppdb_copy:
                self.assignMppdbId(self.action_map[key], self.new_mppdbs)
            elif self.action_map[key][0].action == MigrationJob._tenant_mppdb_data_movement:
                self.assignMppdbId(self.action_map[key], self.new_mppdbs + self.old_mppdbs)

        return

    # We need to assign mppdb id to the MPPDBCopy action object
    def assignMppdbId(self, actions, mppdbs):

        if (len(actions) != len(mppdbs)):
            raise Exception("Size of actions and mppdbs should be same. Something wrong here")

        for i in range(len(actions)):
            actions[i].setDestMppdb(mppdbs[i].mppdb_id)

    def __eq__(self, other):
        if isinstance(other,
                      MPPDBCreation) and self.dest_tenant_mppdb_group.tenant_mppdb_group_id == other.dest_tenant_mppdb_group.tenant_mppdb_group_id and self.mppdb_quantity_to_create == other.mppdb_quantity_to_create:
            return True
        else:
            return False
