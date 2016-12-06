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
import uuid

import concurrent.futures
from sqlalchemy.orm import Session
from threading import Thread

import common.string_constant
from common import constant
from common.db.db_util import SQLalchemyUtil
from common.models import MigrationJob
from deployment_master.migration_job_factory import MigrationJobFactory

deploymentmaster = "deploymentmaster"
queryrouter = "queryrouter"


class JobQueueManager(object):
    logger = logging.getLogger("JobQueueManager")

    thread = None
    close_flag = False
    num_pending_and_running_job = 0

    @classmethod
    def increment_num_pending_and_running_job(cls):
        cls.num_pending_and_running_job += 1

    @classmethod
    def minus_num_pending_and_running_job(cls, future):
        cls.num_pending_and_running_job -= 1

    @classmethod
    def get_migration_lock(cls, session, worker_id):
        try:
            update_query = "update JobQueue set status='"+common.string_constant.TenantUpdateJobStatus_PROCESSING+"', worker_id='" + str(
                worker_id) + "' where status='" + common.string_constant.TenantUpdateJobStatus_PENDING + "' order by last_touch_timestamp limit 1;"
            session.execute(update_query)
            session.commit()

            affected_row = session.query(MigrationJob).filter_by(status=common.string_constant.TenantUpdateJobStatus_PROCESSING).filter_by(worker_id=str(worker_id)).first()

            # There is job in JobQueue
            if affected_row is not None:
                conflictQuery = cls.get_processing_query(session, affected_row.tenant_mppdb_id)
                # There is no confliction with the current job
                if conflictQuery == 0:
                    return affected_row
                # There is confliction with the current job
                else:
                    migrationjob = session.query(MigrationJob).get(affected_row.id)
                    migrationjob.status = common.string_constant.TenantUpdateJobStatus_PENDING
                    migrationjob.workerId = None
                    session.commit()
            # There is no job in JobQueue
            else:
                return None

        except:
            session.rollback()
            raise

    # Endless loop of daemon thread
    @classmethod
    def daemon_check_job_thread(cls):
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=constant.TENANT_UPDATE_JOB_MAX_NUM_THREAD) as update_job_thread_pool:
            while not cls.close_flag:
                session = None
                try:
                    logging.info("Check TenantMPPDB Update Job Queue")
                    session = SQLalchemyUtil.get_session()
                    # threads available
                    if cls.num_pending_and_running_job < constant.TENANT_UPDATE_JOB_MAX_NUM_THREAD:
                        worker_id = uuid.uuid1()
                        job = JobQueueManager.get_migration_lock(session, worker_id)
                        # There is available job
                        if job is not None:
                            cls.increment_num_pending_and_running_job()
                            future = update_job_thread_pool.submit(MigrationJobFactory.getActionRunnable(job))
                            future.add_done_callback(cls.minus_num_pending_and_running_job)

                except Exception:
                    cls.logger.exception("fail to retrieve job")
                    if isinstance(session, Session):
                        session.rollback()
                finally:
                    if isinstance(session, Session):
                        session.close()
                    try:
                        time.sleep(constant.TENANT_UPDATE_JOB_CHECK_INTERVAL_IN_SECOND)
                    except Exception:
                        pass

    @classmethod
    def get_processing_query(cls, session, tenant_mppdb_id):
        counter = 0
        queries = session.query(MigrationJob).filter_by(status=common.string_constant.TenantUpdateJobStatus_PROCESSING, type=queryrouter).all()

        if len(queries) <> 0:
            for query in queries:
                if query.tenant_mppdb_id == tenant_mppdb_id:
                    counter += 1
        return counter

    @classmethod
    def start(cls):
        cls.thread = Thread(target=cls.daemon_check_job_thread)
        cls.thread.start()

    @classmethod
    def stop(cls):
        cls.close_flag = True
        cls.thread.join()


