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

from sqlalchemy.orm import Session

from common.dao import MigrationJobDAO, MPPDBDAO
from common.dao import TenantMPPDBDAO
from common.dao import UserDAO
from common.db.db_util import SQLalchemyUtil
from common.models import MigrationJob
from common.util.vertica_db_operations import move_tenant_mppdb_btw_mppdb
from deployment_master.action import Action


class MPPDBCopy(Action):

    logger = logging.getLogger("MPPDBCopy")

    def __init__(self, migration_job):
        super(MPPDBCopy, self).__init__()
        self.migration_job = migration_job

    def __call__(self):
        self.logger.info('Start to move tenant MPPDB data.')

        self.session = None
        try:
            self.session = SQLalchemyUtil.get_session()

            source_mppdb = MPPDBDAO.get_mppdb(self.session, self.migration_job.source_mppdb_id)
            dest_mppdb = MPPDBDAO.get_mppdb(self.session, self.migration_job.dest_mppdb_id)
            tenant_mppdb = TenantMPPDBDAO.get_tenant_mppdb(self.session, self.migration_job.tenant_mppdb_id)

            # get user names of the tenant_mppdb
            user_list = UserDAO.get_user_list(self.session, tenant_mppdb.tenant_mppdb_id)
            tenant_mppdb.user_list = user_list

            self.logger.info('Start to move tenant MPPDB data.')

            move_tenant_mppdb_btw_mppdb(self.migration_job, source_mppdb, dest_mppdb, tenant_mppdb)

            self.logger.info('Tenant MPPDB data are moved.')

            # Remove the current job from JobQueue table
            job = self.session.query(MigrationJob).filter_by(id=self.migration_job.id).one()
            self.session.delete(job)
            self.session.commit()

            # Check all Tenant MPPDBs in the same group are copied, then the MPPDB is ready for use and so we can update MPPDB record in backend database
            completed = MigrationJobDAO.get_mppdb_copy_completed(self.session, self.migration_job.action, tenant_mppdb.tenant_mppdb_group_id, self.migration_job.dest_mppdb_id)
            if completed == True:
                mppdb = MPPDBDAO.get_mppdb(self.session,dest_mppdb.mppdb_id)
                mppdb.tenant_mppdb_group_id = tenant_mppdb.tenant_mppdb_group_id
                self.session.add(mppdb)
                self.session.commit()

            return
        except Exception:
            self.logger.exception("Fail to execute "+self.__class__.__name__)
            if isinstance(self.session, Session):
                self.session.rollback()
        finally:
            if isinstance(self.session, Session):
                self.session.close()

    def __eq__(self, other):
        if isinstance(other, MPPDBCopy):
            if other.migration_job == self.migration_job:
                return True
            else:
                return False
        return False
