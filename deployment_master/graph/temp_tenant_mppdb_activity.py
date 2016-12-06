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
from common import constant, log
from common.dao import TenantMPPDBActivityDAO
from common.db.db_analyzer import DatabaseAnalyzer

LOG = log.getLogger(__name__)

class TenantMPPDBActivity:

    def __init__(self):
        self.service_level_checker = DatabaseAnalyzer(DatabaseAnalyzer.DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_UPDATING)

    def calculate_tenant_mppdb_activity(self, session):
        try:
            tenantMppdbs = self.service_level_checker.get_tenant_mppdb_list_in_dashboard()
            for tenantMppdb in tenantMppdbs:
                value = tenantMppdb.query_status_list[0]
                # update the TempTenantMPPDBActivity table in the backend database
                TenantMPPDBActivityDAO.update_temp_tenant_mppdb_activity_table(session, self.service_level_checker.analysis_end_time, tenantMppdb.tenant_mppdb_id, value)

        except Exception as e:
            logging.error(e)

