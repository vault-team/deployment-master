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

from common.models import TenantMPPDBGroup, MPPDB
from common.util.trove_cluster_operations import delete_trove_cluster
from deployment_master.action import Action


class MPPDBDeletion(Action):
     def __init__(self, tenant_mppdb_group_id=None):
         self.tenant_mppdb_group_id = tenant_mppdb_group_id

     def run(self,session):
         logging.info('Check the group size of the Tenant MPPDB Group.')
         tenant_mppdb_group=session.query(TenantMPPDBGroup).filter_by(tenant_mppdb_group_id=self.tenant_mppdb_group_id).one()
         if(tenant_mppdb_group.group_size==0):
            logging.info('Start to delete MPPDBs.')

            mppdbs = session.query(MPPDB).filter_by(tenant_mppdb_group_id=self.tenant_mppdb_group_id).all()

            for mppdb in mppdbs:
                delete_trove_cluster(mppdb.mppdb_id)
                session.delete(mppdb)
                session.commit()

            session.delete(tenant_mppdb_group)
            session.commit()

            logging.info('Discarded MPPDBs are deleted.')
         return

     def __eq__(self, other):
         if isinstance(other, MPPDBDeletion) and self.tenant_mppdb_group_id == other.tenant_mppdb_group_id:
             return True
         else:
             return False
