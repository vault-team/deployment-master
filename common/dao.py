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
import common.string_constant
from common.models import MigrationJob, MPPDB, TenantMPPDB, User, TenantMPPDBGroup, Performance, SlaGuarantee, \
    TenantMPPDBActivity, ConsolidationLog


class MigrationJobDAO():
    @staticmethod
    def get_tenant_mppdb_existed_in_jobqueue(session, tenant_mppdb_id):
        jobs = session.query(MigrationJob).filter_by(tenant_mppdb_id=tenant_mppdb_id).all()
        if len(jobs) != 0:
            return True
        # tenant_mppdb has no jobs in job queue
        else:
            return False


    @staticmethod
    # check all MPPDBs of a particular tenant mppdb is already migrated
    def get_tenant_mppdb_migration_ready(session, changes_id):
        job_list = session.query(MigrationJob).filter_by(changes_id=changes_id).all()
        session.commit()
        if len(job_list) == 0:
            return True
        else:
            return False

    @staticmethod
    def get_processing_jobs(session):
        processing_jobs = session.query(MigrationJob).filter_by(status=common.string_constant.TenantUpdateJobStatus_PROCESSING).all()
        session.commit()
        return processing_jobs

    @staticmethod
    # Check all Tenant MPPDBs in the same group are copied, then the MPPDB is ready for use and so we can update MPPDB record in backend database
    def get_mppdb_copy_completed(session, action, tenant_mppdb_group_id, dest_mppdb_id):
        jobQuantity = 0
        tenant_mppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).all()
        session.commit()

        for tenant_mppdb in tenant_mppdbs:
            jobs = session.query(MigrationJob).filter_by(action='mppdb_copy').filter_by(tenant_mppdb_id=tenant_mppdb.tenant_mppdb_id).filter_by(dest_mppdb_id=dest_mppdb_id).all()
            session.commit()
            jobQuantity = jobQuantity + len(jobs)

        if (jobQuantity == 0):
            return True
        else:
            return False

    @staticmethod
    def get_mppdb_move_completed(session, action, tenant_mppdb_group_id, dest_mppdb_id):
        jobQuantity = 0
        tenant_mppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).all()
        session.commit()

        for tenant_mppdb in tenant_mppdbs:
            jobs = session.query(MigrationJob).filter_by(action='tenant_mppdb_data_movement').filter_by(
                tenant_mppdb_id=tenant_mppdb.tenant_mppdb_id).filter_by(dest_mppdb_id=dest_mppdb_id).all()
            session.commit()
            jobQuantity = jobQuantity + len(jobs)

        if (jobQuantity == 0):
            return True
        else:
            return False

class MPPDBDAO():
    @staticmethod
    def get_mppdb_list(session, source_tenant_mppdb_group_id):
        mppdb_list = session.query(MPPDB).filter_by(tenant_mppdb_group_id=source_tenant_mppdb_group_id).all()
        session.commit()
        return mppdb_list

    @staticmethod
    def get_mppdb(session, mppdb_id):
        mppdb = session.query(MPPDB).filter_by(mppdb_id=mppdb_id).one()
        session.commit()
        return mppdb


class TenantMPPDBDAO():
    @staticmethod
    def get_tenant_mppdbs(session, tenant_mppdb_group_id):
        tenant_mppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).all()
        session.commit()
        return tenant_mppdbs

    @staticmethod
    def get_tenant_mppdb(session, tenant_mppdb_id):
        tenant_mppdb = session.query(TenantMPPDB).filter_by(tenant_mppdb_id=tenant_mppdb_id).one()
        session.commit()
        return tenant_mppdb

class TenantMPPDBGroupDAO():
    @staticmethod
    def update_source_tenant_mppdb_group_size(session, source_tenant_mppdb_group_id):
        source_tenant_mppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=source_tenant_mppdb_group_id).all()
        session.commit()
        tenant_mppdb_group = session.query(TenantMPPDBGroup).filter_by(tenant_mppdb_group_id=source_tenant_mppdb_group_id).one()
        session.commit()
        tenant_mppdb_group.group_size = len(source_tenant_mppdbs)
        session.add(tenant_mppdb_group)
        session.commit()

    @staticmethod
    def update_dest_tenant_mppdb_group_size(session, dest_tenant_mppdb_group_id, formation_time, node_quantity, flavor):
        try:
            dest_tenant_mppdbs = session.query(TenantMPPDB).filter_by(
                tenant_mppdb_group_id=dest_tenant_mppdb_group_id).all()
            session.commit()
            tenant_mppdb_group = session.query(TenantMPPDBGroup).filter_by(
                tenant_mppdb_group_id=dest_tenant_mppdb_group_id).one()
            session.commit()
            tenant_mppdb_group.group_size = len(dest_tenant_mppdbs)
            session.add(tenant_mppdb_group)
            session.commit()
        # cannot find the record in tenant mppdb group table since it is a new tmg
        except:
            dest_tenant_mppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=dest_tenant_mppdb_group_id).all()
            session.commit()
            tenant_mppdb_group_record = TenantMPPDBGroup(dest_tenant_mppdb_group_id, len(dest_tenant_mppdbs), formation_time, node_quantity, flavor)
            session.add(tenant_mppdb_group_record)
            session.commit()


class UserDAO():
    @staticmethod
    def get_user_list(session, tenant_mppdb_id):
        user_list = session.query(User).filter_by(tenant_mppdb_id=tenant_mppdb_id).all()
        session.commit()
        return user_list


class PerformanceDAO():
    @staticmethod
    def update_temp_performance_table(session, time, tenant_mppdb_group_id, value):
        performance_record = Performance(time, tenant_mppdb_group_id, value)
        session.add(performance_record)
        session.commit()


class SlaGuaranteeDAO():
    @staticmethod
    def update_temp_sla_guarantee_table(session, time, tenant_mppdb_group_id, value):
        sla_guarantee_record = SlaGuarantee(time, tenant_mppdb_group_id, value)
        session.add(sla_guarantee_record)
        session.commit()


class TenantMPPDBActivityDAO():
    @staticmethod
    def update_temp_tenant_mppdb_activity_table(session, time, tenant_mppdb_id, value):
        tenant_mppdb_activity_record = TenantMPPDBActivity(time, tenant_mppdb_id, value)
        session.add(tenant_mppdb_activity_record)
        session.commit()


class ConsolidationLogDAO():
    @staticmethod
    def update_consolidation_log_table(session, last_timestamp):
        consolidation_log_record = ConsolidationLog(last_timestamp)
        session.add(consolidation_log_record)
        session.commit()