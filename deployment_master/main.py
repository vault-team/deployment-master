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

import threading
import time
import schedule as schedule
from common import log
from common.constant import SERVICE_LEVEL_CHECKING_PERIOD, CONSOLIDATION_PERIOD
from deployment_master.graph_data_manager import GraphDataManager
from deployment_master.job_queue_manager import JobQueueManager
from deployment_master.logic import DeploymentMaster
from service_level_monitor import ServiceLevelMonitor

logger = log.getLogger(__name__)


class Main:
    deployment_master = DeploymentMaster()
    sla_monitor = ServiceLevelMonitor()
    thread_consolidation = None
    thread_sla_monitor = None

    @classmethod
    def job_redeploy(cls):
        """Trigger consolidation and redeployment"""
        if cls.thread_consolidation is not None and isinstance(cls.thread_consolidation, threading.Thread):
            cls.thread_consolidation.join()
        logger.info("Start system consolidation")
        cls.thread_consolidation = threading.Thread(target=cls.deployment_master.redeploy, name="System consolidation")
        cls.thread_consolidation.start()


    @classmethod
    def job_sla_monitor(cls):
        """Trigger service level checking"""
        if cls.thread_sla_monitor is not None and isinstance(cls.thread_sla_monitor, threading.Thread):
            cls.thread_sla_monitor.join()
        logger.info("Start SLA monitor")
        cls.thread_sla_monitor = threading.Thread(target=cls.sla_monitor.ensure_service_level, name="SLA monitor")
        cls.thread_sla_monitor.start()

    @classmethod
    def start(cls):
        schedule.every(CONSOLIDATION_PERIOD.total_seconds()).seconds.do(cls.job_redeploy)
        schedule.every(SERVICE_LEVEL_CHECKING_PERIOD.total_seconds()).seconds.do(cls.job_sla_monitor)
        #JobQueueManager.start()
        GraphDataManager.start()
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                break
        cls.exit()

    @classmethod
    def exit(cls):
        JobQueueManager.stop()
        GraphDataManager.stop()

# Main
if __name__ == "__main__":
    logger.info("Starting vault")
    Main.start()
