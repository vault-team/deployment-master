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

from common.dao import TenantMPPDBDAO, UserDAO, MPPDBDAO, MigrationJobDAO
from common.db.db_util import SQLalchemyUtil
from common.util.vertica_db_operations import delete_user
from deployment_master.action import Action


class TenantMPPDBDataDeletion(Action):
    def __init__(self, tenant_mppdb_id=None):
        self.tenant_mppdb_id = tenant_mppdb_id
        self.existed = False

    def run(self):
        logging.info('Start to delete tenant MPPDB data.')
        session = SQLalchemyUtil.get_session()

        user_list = UserDAO.get_user_list(session, self.tenant_mppdb_id)

        tenant_mppdb = TenantMPPDBDAO.get_tenant_mppdb(session, self.tenant_mppdb_id)

        mppdb_list = MPPDBDAO.get_mppdb_list(session, tenant_mppdb.tenant_mppdb_group_id)

        while True:
            # find out whether the tenant_mppdbs have jobs in job queue
            existed = MigrationJobDAO.get_tenant_mppdb_existed_in_jobqueue(session, tenant_mppdb.tenant_mppdb_id)
            if existed is False:
                for mppdb in mppdb_list:
                    if len(user_list) != 0:
                        delete_user(mppdb.mppdb_ip, mppdb.mppdb_password, user_list)


                logging.info('Tenant MPPDB data are deleted.')
                break

