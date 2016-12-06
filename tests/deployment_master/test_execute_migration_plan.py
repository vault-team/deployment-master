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

from unittest import TestCase

from common.db.db_util import SQLalchemyUtil
from common.models import MPPDB, TenantMPPDB, TenantMPPDBGroup, User
from deployment_master import job_queue_manager
from deployment_master.job_queue_manager import JobQueueManager
from deployment_master.main import DeploymentMaster, Main
from tests.deployment_master.test_deploymentmaster_reset import test_deploymentmaster_reset
import unittest


#######################################Unit Test 3#####################################

##########################################Aim##########################################
# After the migration plan is generated, the action will now be recorded into the JobQueue table in backend-database
# The actions will be executed using the thread
######################################Prerequisite#####################################
# The prerequisite specified in Unit Test 1 and 2
# Remove the previous testing result in the MPPDB (192.168.1.203, 205, 218, 226)
# for example =>drop user tm6_Billy cascade;
# check whether the user (select user_name from users;) or tables (\d) exists in the MPPDB
#####################################Expected Output###################################
# Case 1:
# TenantMPPDB 1 is moved to 218 (new TG4) and data on 220 is removed
# TG1 is copied to 203 with TenantMPPDB 3,6
# TG2 is copied to 226 with TenantMPPDB 2,5
#
# Case 2:
# TenantMPPDB 1 data is moved to 210 and 220 is removed
# TG1 is copied to 203 with TenantMPPDB 3,6
# TG2 is copied to 226 with TenantMPPDB 2,5
# TG3 is copied to 205 with TenantMPPDB 1,4
########################################################################################

class MigrationPlanGenerationTest(unittest.TestCase):
    """""""""
    def test_execute_migration_plan_case1(self):
        # Prepare source Mppdb cluster, TenantMPPDBData (include System db, Actual vertica DB, Tenant MPPDB
        # Prepare destination MPPDB cluster

        ##############################Test Case 1################################
        # CREATE MPPDB and Tenant MPPDB Group for Tenant MPPDB Group 4
        # CREATE and COPY the MPPDB when the quantity of MPPDBs of a TenantMPPDBGroup is fewer than the replication factor (copy tmg1: 192.168.1.203, tmg2: 192.168.1.226)
        # MOVE Tenant MPPDB 1 data from the MPPDBs in Tenant MPPDB Group 1 to Tenant MPPDB Group 4 and update the backend database (move tmg1 to tmg4: from 192.168.1.220 to 192.168.1.218)
        # DELETE the data of Tenant MPPDB 1 in Tenant MPPDB Group 1

        new_tenant_mppdb_group_list_case1 = [TenantMPPDBGroup(2, 2, '2016-07-20 11:34:41.727016', 1, '8', [
            TenantMPPDB(5, 2, '1', '8', '7d060ae439ad469a9729cfaedfe264d6', 'Math',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1]',
                        '0.108333333333', [User('7', 'Michael', 'admin', 'michael123', '5')]),
            TenantMPPDB(2, 2, '1', '8', '43aad64fa7c244e69246b596b6c19128', 'Engineering',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.125', [User('1', 'Peter', 'admin', 'peter123', '2'),
                                  User('3', 'Sally', 'admin', 'sally123', '2')])], [
                                                                  MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df ',
                                                                        '192.168.1.213', '2', '')]),
                                             TenantMPPDBGroup(1, 2, '2016-07-20 11:34:41.727016', 1, '7', [
                                                 TenantMPPDB(3, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128',
                                                             'Statistics',
                                                             '[0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                             '0.108333333333',
                                                             [User('4', 'Mary', 'admin', 'mary123', '3')]),
                                                 TenantMPPDB(6, 1, '1', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                             'Physics',
                                                             '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                             '0.108333333333',
                                                             [User('5', 'Billy', 'admin', 'billy123', '6')])], [
                                                                  MPPDB('ffae3bc8-572a-4a10-aeae-048bd4e9f9f2',
                                                                        '192.168.1.220', '1', '')]),
                                             TenantMPPDBGroup(3, 1, '2016-07-20 11:34:41.727016', 2, '7', [
                                                 TenantMPPDB(4, 3, '2', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                             'Chemistry',
                                                             '[0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0]',
                                                             '0.2',
                                                             [User('6', 'Henry', 'admin', 'henry123', '4')])], [
                                                                  MPPDB('e6e53153-336f-4030-bd33-10f99bd159e5',
                                                                        '192.168.1.210', '3', '')]),
                                             TenantMPPDBGroup(4, 1, '2016-07-20 11:34:41.727016', 1, '7', [
                                                 TenantMPPDB(1, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128',
                                                             'Computing',
                                                             '[1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                             '0.208333333333',
                                                             [User('2', 'John', 'admin', 'john123', '1')])],
                                                              'None')]

        ##############################The current_tenant_mppdb_group_list will be used in Test Case 1 and 2##############################
        current_tenant_mppdb_group_list = [TenantMPPDBGroup(1, 3, '2016-07-19 17:08:52.782331', 1, '7', [
            TenantMPPDB(1, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128', 'Computing',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.0333333333333', [User('2', 'John', 'admin', 'john123', '1')]),
            TenantMPPDB(6, 1, '1', '7', '7d060ae439ad469a9729cfaedfe264d6', 'Physics',
                        '[0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.05', [User('5', 'Billy', 'admin', 'billy123', '6')]),
            TenantMPPDB(3, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128', 'Statistics',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.075', [User('4', 'Mary', 'admin', 'mary123', '3')])], [
                                                                MPPDB('ffae3bc8-572a-4a10-aeae-048bd4e9f9f2',
                                                                      '192.168.1.220', '1', '')]),
                                           TenantMPPDBGroup(2, 2, '2016-07-19 17:08:52.782331', 1, '8', [
                                               TenantMPPDB(5, 2, '1', '8', '7d060ae439ad469a9729cfaedfe264d6', 'Math',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0',
                                                           [User('7', 'Michael', 'admin', 'michael123', '5')]),
                                               TenantMPPDB(2, 2, '1', '8', '43aad64fa7c244e69246b596b6c19128',
                                                           'Engineering',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0166666666667',
                                                           [User('1', 'Peter', 'admin', 'peter123', '2'),
                                                            User('3', 'Sally', 'admin', 'sally123', '2')])], [
                                                                MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df ',
                                                                      '192.168.1.213', '2', '')]),
                                           TenantMPPDBGroup(3, 1, '2016-07-19 17:08:52.782331', 2, '7', [
                                               TenantMPPDB(4, 3, '2', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                           'Chemistry',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0583333333333',
                                                           [User('6', 'Henry', 'admin', 'henry123', '4')])], [
                                                                MPPDB('e6e53153-336f-4030-bd33-10f99bd159e5',
                                                                      '192.168.1.210', '3', '')])]

        dm = DeploymentMaster()
        test_deploymentmaster_reset.reset()

        migration_plan = dm.generate_migration_plan(current_tenant_mppdb_group_list, new_tenant_mppdb_group_list_case1)
        session = SQLalchemyUtil.get_session()
        dm.execute_migration_plan(session, migration_plan, 1)
        JobQueueManager.start()

    """
    def test_execute_migration_plan_case2(self):
        ##############################The current_tenant_mppdb_group_list will be used in Test Case 1 and 2##############################
        current_tenant_mppdb_group_list = [TenantMPPDBGroup(1, 3, '2016-07-19 17:08:52.782331', 1, '7', [
            TenantMPPDB(1, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128', 'Computing',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.0333333333333', [User('2', 'John', 'admin', 'john123', '1')]),
            TenantMPPDB(6, 1, '1', '7', '7d060ae439ad469a9729cfaedfe264d6', 'Physics',
                        '[0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.05', [User('5', 'Billy', 'admin', 'billy123', '6')]),
            TenantMPPDB(3, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128', 'Statistics',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.075', [User('4', 'Mary', 'admin', 'mary123', '3')])], [
                                                                MPPDB('ffae3bc8-572a-4a10-aeae-048bd4e9f9f2',
                                                                      '192.168.1.220', '1', '')]),
                                           TenantMPPDBGroup(2, 2, '2016-07-19 17:08:52.782331', 1, '8', [
                                               TenantMPPDB(5, 2, '1', '8', '7d060ae439ad469a9729cfaedfe264d6', 'Math',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0',
                                                           [User('7', 'Michael', 'admin', 'michael123', '5')]),
                                               TenantMPPDB(2, 2, '1', '8', '43aad64fa7c244e69246b596b6c19128',
                                                           'Engineering',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0166666666667',
                                                           [User('1', 'Peter', 'admin', 'peter123', '2'),
                                                            User('3', 'Sally', 'admin', 'sally123', '2')])], [
                                                                MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df ',
                                                                      '192.168.1.213', '2', '')]),
                                           TenantMPPDBGroup(3, 1, '2016-07-19 17:08:52.782331', 2, '7', [
                                               TenantMPPDB(4, 3, '2', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                           'Chemistry',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0583333333333',
                                                           [User('6', 'Henry', 'admin', 'henry123', '4')])], [
                                                                MPPDB('e6e53153-336f-4030-bd33-10f99bd159e5',
                                                                      '192.168.1.210', '3', '')])]
        ##############################Test Case 2################################
        # CREATE and COPY the MPPDB when the quantity of MPPDBs of a TenantMPPDBGroup is fewer than the replication factor (copy tmg1: 192.168.1.203, tmg2: 192.168.1.226, tmg3: 192.168.1.205)
        # MOVE Tenant MPPDB 1 data from the MPPDBs in Tenant MPPDB Group 1 to Tenant MPPDB Group 3 and update the backend database (if move action before tmg3 copy: move from 192.168.1.220 to 192.168.1.210 / if move action after copy tmg3: move from 192.168.1.220 to 192.168.1.210 and 205)
        # DELETE the data of Tenant MPPDB 1 in Tenant MPPDB Group 1 (delete the tmg 1 data in 192.168.1.220)
        new_tenant_mppdb_group_list_case2 = [TenantMPPDBGroup(2, 2, '2016-07-20 11:34:41.727016', 1, '8', [
            TenantMPPDB(5, 2, '1', '8', '7d060ae439ad469a9729cfaedfe264d6', 'Math',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1]',
                        '0.108333333333', [User('7', 'Michael', 'admin', 'michael123', '5')]),
            TenantMPPDB(2, 2, '1', '8', '43aad64fa7c244e69246b596b6c19128', 'Engineering',
                        '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                        '0.125', [User('1', 'Peter', 'admin', 'peter123', '2'),
                                  User('3', 'Sally', 'admin', 'sally123', '2')])], [
                                                                  MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df ',
                                                                        '192.168.1.213', '2', '')]),
                                             TenantMPPDBGroup(1, 2, '2016-07-20 11:34:41.727016', 1, '7', [
                                                 TenantMPPDB(3, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128',
                                                             'Statistics',
                                                             '[0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                             '0.108333333333',
                                                             [User('4', 'Mary', 'admin', 'mary123', '3')]),
                                                 TenantMPPDB(6, 1, '1', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                             'Physics',
                                                             '[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                             '0.108333333333',
                                                             [User('5', 'Billy', 'admin', 'billy123', '6')])], [
                                                                  MPPDB('ffae3bc8-572a-4a10-aeae-048bd4e9f9f2',
                                                                        '192.168.1.220', '1', '')]),
                                             TenantMPPDBGroup(3, 1, '2016-07-20 11:34:41.727016', 2, '7', [
                                                 TenantMPPDB(4, 3, '2', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                             'Chemistry',
                                                             '[0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0]',
                                                             '0.2', [User('6', 'Henry', 'admin', 'henry123', '4')]),
                                                 TenantMPPDB(1, 1, '1', '7', '43aad64fa7c244e69246b596b6c19128',
                                                             'Computing',
                                                             '[1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                             '0.208333333333',
                                                             [User('2', 'John', 'admin', 'john123', '1')])], [
                                                                  MPPDB('e6e53153-336f-4030-bd33-10f99bd159e5',
                                                                        '192.168.1.210', '3', '')])]

        dm = DeploymentMaster()
        test_deploymentmaster_reset.reset()

        migration_plan = dm.generate_migration_plan(current_tenant_mppdb_group_list, new_tenant_mppdb_group_list_case2)
        session = SQLalchemyUtil.get_session()
        dm.execute_migration_plan(session, migration_plan, 2)
        JobQueueManager.start()


if __name__ == '__main__':
    unittest.main()