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
from datetime import datetime

from sqlalchemy.orm import Session

from common import constant
from common.dao import MigrationJobDAO, MPPDBDAO, TenantMPPDBGroupDAO
from common.dao import TenantMPPDBDAO
from common.dao import UserDAO
from common.db.db_util import SQLalchemyUtil
from common.models import MigrationJob, TenantMPPDBGroup
from common.util.vertica_db_operations import move_tenant_mppdb_btw_mppdb, delete_user, find_users
from deployment_master.action import Action
from deployment_master.action.mppdb_deletion import MPPDBDeletion

logger = logging.getLogger("TenantMPPDBDataMovement")


class TenantMPPDBDataMovement(Action):
    def __init__(self, migration_job):
        super(TenantMPPDBDataMovement, self).__init__()
        self.migration_job = migration_job

    def __call__(self):

        logger.info("Start move tenant mppdb data")
        self.session = None
        try:
            self.session = SQLalchemyUtil.get_session()
            source_mppdb = MPPDBDAO.get_mppdb(self.session, self.migration_job.source_mppdb_id)
            dest_mppdb = MPPDBDAO.get_mppdb(self.session, self.migration_job.dest_mppdb_id)
            tenant_mppdb = TenantMPPDBDAO.get_tenant_mppdb(self.session, self.migration_job.tenant_mppdb_id)
            # get user names of the tenant
            user_list = UserDAO.get_user_list(self.session, tenant_mppdb.tenant_mppdb_id)
            tenant_mppdb.user_list = user_list

            logger.info('Start to move tenant MPPDB data.')
            move_tenant_mppdb_btw_mppdb(self.migration_job, source_mppdb, dest_mppdb, tenant_mppdb)
            logger.info('Tenant MPPDB data are moved.')

            # Remove the current job from JobQueue table
            job = self.session.query(MigrationJob).filter_by(id=self.migration_job.id).one()
            self.session.delete(job)
            self.session.commit()

            # check all MPPDBs of a particular tenant mppdb is already migrated
            tenant_mppdb_migration_ready = MigrationJobDAO.get_tenant_mppdb_migration_ready(self.session,
                                                                                            self.migration_job.changes_id)
            if tenant_mppdb_migration_ready == False:
                return

            # After checking, update the tenant mppdb's tenant_mppdb_group_id
            tenant_mppdb.tenant_mppdb_group_id = dest_mppdb.tenant_mppdb_group_id
            self.session.add(tenant_mppdb)
            self.session.commit()

            TenantMPPDBGroupDAO.update_dest_tenant_mppdb_group_size(self.session, dest_mppdb.tenant_mppdb_group_id, None, constant.REPLICATON_FACTOR, tenant_mppdb.flavor)

            logger.info('The tenant MPPDB groups info is updated in the system database.')

            logger.info('Start to delete tenant MPPDB data.')
            user_list = tenant_mppdb.user_list
            source_mppdb_list = MPPDBDAO.get_mppdb_list(self.session, source_mppdb.tenant_mppdb_group_id)

            # delete users in mppdbs
            # check whether the target mppdb has those users, if yes, it will delete those users
            for source_mppdb in source_mppdb_list:
                check = False
                users_in_db = find_users(source_mppdb.mppdb_ip, source_mppdb.mppdb_password)
                for user in user_list:
                    user_name = user.get_sql_username()
                    for user_in_db in users_in_db:
                        if user_name == user_in_db:
                            check = True
                if check == True:
                    delete_user(source_mppdb.mppdb_ip, source_mppdb.mppdb_password, user_list)
            logger.info('Tenant MPPDB data are deleted.')

            TenantMPPDBGroupDAO.update_source_tenant_mppdb_group_size(self.session, source_mppdb.tenant_mppdb_group_id)
            self.session.commit()

            action_delete = MPPDBDeletion(source_mppdb.tenant_mppdb_group_id)
            action_delete.run(self.session)
            return
        except Exception as inst:
            logger.debug('tenant_mppdb_data_movement: ')
            logger.debug(inst)
            logger.exception()
            if isinstance(self.session, Session):
                self.session.rollback()
        finally:
            if isinstance(self.session, Session):
                self.session.close()

    def __eq__(self, other):
        if isinstance(other, TenantMPPDBDataMovement):
            if other.migration_job == self.migration_job:
                return True
            else:
                return False
        return False
