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

from common.models import MPPDB


class mppdb_creation_dictionary_for_testing(object):
    ############################################################################Test case 1##############################################################################################################
    # ignore the new mppdb and find those old_mppdbs
    @classmethod
    def find_old_mppdbs_test_case1(cls, dest_tenant_mppdb_group):
        old_mppdbs = []
        if dest_tenant_mppdb_group.tenant_mppdb_group_id == 1:
            mppdb = MPPDB(mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', mppdb_ip='192.168.1.220',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 2:
            mppdb = MPPDB(mppdb_id='8b029e34-55c4-4b84-b336-8ac7fe60e6df', mppdb_ip='192.168.1.213',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 3:
            mppdb = MPPDB(mppdb_id='e6e53153-336f-4030-bd33-10f99bd159e5', mppdb_ip='192.168.1.210',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
        if dest_tenant_mppdb_group.tenant_mppdb_group_id <> 4:
            old_mppdbs.append(mppdb)
        return old_mppdbs

    # skip to create the MPPDBs for simulating mppdb copy
    @classmethod
    def find_new_mppdbs_test_case1(cls, dest_tenant_mppdb_group):
        new_mppdbs = []
        if dest_tenant_mppdb_group.tenant_mppdb_group_id == 1:
            mppdb = MPPDB(mppdb_id='530807a9-d428-4d69-83b2-9fad30189d7b', mppdb_ip='192.168.1.203',
                          tenant_mppdb_group_id=-1, mppdb_password='')
            new_mppdbs.append(mppdb)
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 2:
            mppdb = MPPDB(mppdb_id='aff1849f-6cc8-491c-aca5-8e6ef97cf075', mppdb_ip='192.168.1.226',
                          tenant_mppdb_group_id=-1, mppdb_password='')
            new_mppdbs.append(mppdb)
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 3:
            mppdb = MPPDB(mppdb_id='26211c60-c617-4132-9df9-cd40b307caca', mppdb_ip='192.168.1.205',
                          tenant_mppdb_group_id=-1, mppdb_password='')
            new_mppdbs.append(mppdb)
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 4:
            mppdb = MPPDB(mppdb_id='dd669e86-2593-4d7b-b515-52a043824b3a', mppdb_ip='192.168.1.218',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
            new_mppdbs.append(mppdb)
        return new_mppdbs

    #######################################################################################################################################################################################################

    ############################################################################Test case 2##############################################################################################################
    # ignore the new mppdb and find those old_mppdbs
    @classmethod
    def find_old_mppdbs_test_case2(cls, dest_tenant_mppdb_group):
        old_mppdbs = []
        if dest_tenant_mppdb_group.tenant_mppdb_group_id == 1:
            mppdb = MPPDB(mppdb_id='ffae3bc8-572a-4a10-aeae-048bd4e9f9f2', mppdb_ip='192.168.1.220',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 2:
            mppdb = MPPDB(mppdb_id='8b029e34-55c4-4b84-b336-8ac7fe60e6df', mppdb_ip='192.168.1.213',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 3:
            mppdb = MPPDB(mppdb_id='e6e53153-336f-4030-bd33-10f99bd159e5', mppdb_ip='192.168.1.210',
                          tenant_mppdb_group_id=dest_tenant_mppdb_group.tenant_mppdb_group_id, mppdb_password='')
        old_mppdbs.append(mppdb)
        return old_mppdbs

    # skip to create the MPPDBs for simulating mppdb copy
    @classmethod
    def find_new_mppdbs_test_case2(cls, dest_tenant_mppdb_group):
        new_mppdbs = []
        if dest_tenant_mppdb_group.tenant_mppdb_group_id == 1:
            mppdb = MPPDB(mppdb_id='530807a9-d428-4d69-83b2-9fad30189d7b', mppdb_ip='192.168.1.203',
                          tenant_mppdb_group_id=-1, mppdb_password='')
            new_mppdbs.append(mppdb)
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 2:
            mppdb = MPPDB(mppdb_id='aff1849f-6cc8-491c-aca5-8e6ef97cf075', mppdb_ip='192.168.1.226',
                          tenant_mppdb_group_id=-1, mppdb_password='')
            new_mppdbs.append(mppdb)
        elif dest_tenant_mppdb_group.tenant_mppdb_group_id == 3:
            mppdb = MPPDB(mppdb_id='26211c60-c617-4132-9df9-cd40b307caca', mppdb_ip='192.168.1.205',
                          tenant_mppdb_group_id=-1, mppdb_password='')
            new_mppdbs.append(mppdb)
        return new_mppdbs

        #######################################################################################################################################################################################################
