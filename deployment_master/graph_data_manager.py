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
from threading import Thread
import concurrent.futures
import time
import concurrent

from common import constant
from deployment_master.graph.update_graph_data import UpdateGraphData


class GraphDataManager(object):

    logger = logging.getLogger("GraphDataManager")
    thread = None
    close_flag = False

    # Endless loop of daemon thread
    @classmethod
    def daemon_update_table_thread(cls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as update_table_thread_pool:
            while not cls.close_flag:
                try:
                    logging.info("Check TenantMPPDB Update table")
                    future = update_table_thread_pool.submit(UpdateGraphData())

                except Exception:
                    cls.logger.exception("fail to update graph table")
                finally:
                    try:
                        time.sleep(constant.DASHBOARD_UPDATE_GRAPH_DATA_CHECK_INTERVAL_IN_SECOND)
                    except Exception:
                        pass

    @classmethod
    def start(cls):
        cls.thread = Thread(target=cls.daemon_update_table_thread)
        cls.thread.start()

    @classmethod
    def stop(cls):
        cls.close_flag = True
        cls.thread.join()