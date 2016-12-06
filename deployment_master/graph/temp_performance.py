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
from common import constant
from common import log
from common.dao import PerformanceDAO
from common.db.db_analyzer import DatabaseAnalyzer, \
    calculate_active_tenant_mppdbs_count_in_one_epoch

logger = log.getLogger(__name__)

class Performance:

    def __init__(self):
        self.service_level_checker = DatabaseAnalyzer(DatabaseAnalyzer.DASHBOARD_PERFORMANCE_GRAPH_UPDATING)

    def calculate_performance(self, session):

        try:
            tenant_mppdb_groups = self.service_level_checker.get_current_tenant_mppdb_group_list_in_dashboard()

            for tenant_mppdb_group in tenant_mppdb_groups:
                tenant_mppdb_set = tenant_mppdb_group.tenant_mppdb_members_list

                if len(tenant_mppdb_set) != 0:
                    active_tenant_mppdbs_count_in_one_epoch = calculate_active_tenant_mppdbs_count_in_one_epoch(tenant_mppdb_set)

                    mppdb_list = self.service_level_checker.get_mppdb(tenant_mppdb_group.tenant_mppdb_group_id)
                    no_of_mppdbs = len(mppdb_list)

                    if no_of_mppdbs > 0:
                        if active_tenant_mppdbs_count_in_one_epoch < no_of_mppdbs:
                            performance = 1
                        else:
                            performance = float(active_tenant_mppdbs_count_in_one_epoch) / no_of_mppdbs

                        #update the TempPerformance table in the backend database
                        PerformanceDAO.update_temp_performance_table(session, self.service_level_checker.analysis_end_time, tenant_mppdb_group.tenant_mppdb_group_id, performance)

        except Exception as e:
            logger.exception(e)
            raise



