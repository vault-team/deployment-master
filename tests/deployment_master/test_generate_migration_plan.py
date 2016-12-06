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

from common.models import MigrationJob, MPPDB, TenantMPPDB, TenantMPPDBGroup, User
from deployment_master.action.mppdb_creation import MPPDBCreation
from deployment_master.action.tenant_mppdb_group_creation import TenantMPPDBGroupCreation
from deployment_master.main import DeploymentMaster
from deployment_master.models import MigrationPlan


class MigrationPlanGenerationTest(TestCase):
    def test_generate_migration_plan_case1(self):
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
                                                                MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df',
                                                                      '192.168.1.213', '2', '')]),
                                           TenantMPPDBGroup(3, 1, '2016-07-19 17:08:52.782331', 2, '7', [
                                               TenantMPPDB(4, 3, '2', '7', '7d060ae439ad469a9729cfaedfe264d6',
                                                           'Chemistry',
                                                           '[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]',
                                                           '0.0583333333333',
                                                           [User('6', 'Henry', 'admin', 'henry123', '4')])], [
                                                                MPPDB('e6e53153-336f-4030-bd33-10f99bd159e5',
                                                                      '192.168.1.210', '3', '')])]

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
                                                                  MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df',
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

        dm = DeploymentMaster()
        migration_plan = dm.generate_migration_plan(current_tenant_mppdb_group_list, new_tenant_mppdb_group_list_case1)

        # Test Case 1:
        # Actions includes:
        # CreateMPPDB Action for TenantMPPDBGroup 1, 2 and 4 [Node quantity : 2]
        # Create new Tenant MPPDB Group 4
        # Move Tenant MPPDB 1 data from TenantMPPDBGroup 1 to the new TenantMPPDBGroup 4
        # Copy MPPDB in Tenant MPPDB Group 1 (2 times), 2 (2 times)
        # Total 9 actions
        expected_cases = MigrationPlan([
            MPPDBCreation(dest_tenant_mppdb_group=TenantMPPDBGroup(tenant_mppdb_group_id=1),
                          mppdb_quantity_to_create=1,
                          action=MigrationJob._mppdb_copy),
            MPPDBCreation(dest_tenant_mppdb_group=TenantMPPDBGroup(tenant_mppdb_group_id=2),
                          mppdb_quantity_to_create=1,
                          action=MigrationJob._mppdb_copy),
            MPPDBCreation(dest_tenant_mppdb_group=TenantMPPDBGroup(tenant_mppdb_group_id=4),
                          mppdb_quantity_to_create=1,
                          action=MigrationJob._tenant_mppdb_data_movement),
            TenantMPPDBGroupCreation(TenantMPPDBGroup(node_quantity=1)),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', tenant_mppdb_id=1,
                         action=MigrationJob._tenant_mppdb_data_movement),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', tenant_mppdb_id=3,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', tenant_mppdb_id=6,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='8b029e34-55c4-4b84-b336-8ac7fe60e6df', tenant_mppdb_id=2,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='8b029e34-55c4-4b84-b336-8ac7fe60e6df', tenant_mppdb_id=5,
                         action=MigrationJob._mppdb_copy)
        ])

        self.assertEqual(migration_plan, expected_cases)

        # for action in migration_plan.actions:
        #     for action in migration_plan.actions:
        #         if isinstance(action, MigrationJob):
        #         print str(action.__class__) + ", " + str(action.action)
        #     else:
        #         print action.__class__

    def test_generate_migration_plan_case2(self):
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
                                                                MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df',
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
                                                                  MPPDB('8b029e34-55c4-4b84-b336-8ac7fe60e6df',
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
        migration_plan = dm.generate_migration_plan(current_tenant_mppdb_group_list, new_tenant_mppdb_group_list_case2)

        # Test Case 2:
        # Actions includes:
        # CreateMPPDB Action for TenantMPPDBGroup 1, 2 and 3
        # Move Tenant MPPDB 1 data from TenantMPPDBGroup 1 to the TenantMPPDBGroup 3 (1 time)
        # Copy MPPDB in Tenant MPPDB Group 1 (2 times), 2 (2 times), 3 (2 times)
        # CreateMPPDB Action for TenantMPPDBGroup 1 (192.168.1.203, for mppdb copy use), 2 (192.168.1.226, for mppdb copy use) and 4(192.168.1.218, for tenant mppdb data movement)

        expected_cases = MigrationPlan([
            MPPDBCreation(dest_tenant_mppdb_group=TenantMPPDBGroup(tenant_mppdb_group_id=1),
                          mppdb_quantity_to_create=1,
                          action=MigrationJob._mppdb_copy),
            MPPDBCreation(dest_tenant_mppdb_group=TenantMPPDBGroup(tenant_mppdb_group_id=2),
                          mppdb_quantity_to_create=1,
                          action=MigrationJob._mppdb_copy),
            MPPDBCreation(dest_tenant_mppdb_group=TenantMPPDBGroup(tenant_mppdb_group_id=3),
                          mppdb_quantity_to_create=1,
                          action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2',
                         dest_mppdb_id='e6e53153-336f-4030-bd33-10f99bd159e5', tenant_mppdb_id=1,
                         action=MigrationJob._tenant_mppdb_data_movement),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', tenant_mppdb_id=1,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='8b029e34-55c4-4b84-b336-8ac7fe60e6df', tenant_mppdb_id=2,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', tenant_mppdb_id=3,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='e6e53153-336f-4030-bd33-10f99bd159e5', tenant_mppdb_id=4,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='8b029e34-55c4-4b84-b336-8ac7fe60e6df', tenant_mppdb_id=5,
                         action=MigrationJob._mppdb_copy),
            MigrationJob(source_mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', tenant_mppdb_id=6,
                         action=MigrationJob._mppdb_copy),

        ])

        self.assertEqual(migration_plan, expected_cases)
